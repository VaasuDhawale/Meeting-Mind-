import axios from 'axios';
import type { MeetingSession } from './types';

const API_BASE = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Accept': 'application/json',
  },
});

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await apiClient.get('/health');
    return res.data?.status === 'healthy' || res.data?.status === 'degraded';
  } catch {
    return false;
  }
}

export async function getSessions(): Promise<MeetingSession[]> {
  const res = await apiClient.get<MeetingSession[]>('/sessions');
  return res.data;
}

export async function getSession(id: string): Promise<MeetingSession> {
  const res = await apiClient.get<MeetingSession>(`/sessions/${id}`);
  return res.data;
}

export async function analyzeSession(formData: FormData): Promise<MeetingSession> {
  const res = await apiClient.post<MeetingSession>('/sessions/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 180000, // 3 minutes timeout for heavy multimodal media
  });
  return res.data;
}

export async function runFacultyDemo(): Promise<MeetingSession> {
  const res = await apiClient.post<MeetingSession>('/sessions/demo', {}, {
    timeout: 120000,
  });
  return res.data;
}

export async function deleteSession(id: string): Promise<void> {
  await apiClient.delete(`/sessions/${id}`);
}

export function getPdfDownloadUrl(id: string, inline: boolean = false): string {
  return `${API_BASE}/sessions/${id}/pdf${inline ? '?inline=true' : ''}`;
}

export function getTranscriptPdfUrl(id: string, inline: boolean = false): string {
  return `${API_BASE}/sessions/${id}/transcript-pdf${inline ? '?inline=true' : ''}`;
}

export function getTranscriptTxtUrl(id: string): string {
  return `${API_BASE}/sessions/${id}/transcript-txt`;
}

export function getJsonExportUrl(id: string): string {
  return `${API_BASE}/sessions/${id}/json`;
}

export function getMarkdownExportUrl(id: string): string {
  return `${API_BASE}/sessions/${id}/markdown`;
}

export function getDocxDownloadUrl(id: string): string {
  return `${API_BASE}/sessions/${id}/docx`;
}

export function getTextReportUrl(id: string): string {
  return `${API_BASE}/sessions/${id}/txt`;
}

/**
 * Downloads a file using native fetch() to bypass axios baseURL double-prepend.
 * Validates response.ok and Content-Type before creating the Blob and triggering anchor download.
 */
export async function downloadFileBlob(url: string, defaultFilename: string): Promise<void> {
  // 1. Request the correct existing endpoint
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, */*' },
  });

  // 2. Check response.ok
  if (!response.ok) {
    let errorDetail = `HTTP ${response.status} ${response.statusText}`;
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) errorDetail = String(errorBody.detail);
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  // 3. Check that the response is not a JSON error or HTML page
  const contentType = (response.headers.get('content-type') || '').toLowerCase();
  if (contentType.includes('application/json') && !defaultFilename.endsWith('.json')) {
    let errorDetail = 'Server returned a JSON response instead of a binary document.';
    try {
      const errorBody = await response.json();
      if (errorBody?.detail) errorDetail = String(errorBody.detail);
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  if (contentType.includes('text/html')) {
    throw new Error('Server returned an HTML page instead of the requested document.');
  }

  // Extract server-provided filename from Content-Disposition if available
  let resolvedFilename = defaultFilename;
  const contentDisposition = response.headers.get('content-disposition') || '';
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\r\n]+)["']?/i);
    if (filenameMatch && filenameMatch[1]) {
      const parsedName = decodeURIComponent(filenameMatch[1].trim());
      if (parsedName) {
        resolvedFilename = parsedName;
      }
    }
  }

  // 4. Read response as Blob
  const rawBlob = await response.blob();

  // 5. Verify the Blob is not empty
  if (rawBlob.size === 0) {
    throw new Error('Downloaded document is empty (0 bytes).');
  }

  // Ensure explicit binary MIME type on the Blob
  let mimeType = rawBlob.type;
  if (resolvedFilename.toLowerCase().endsWith('.pdf')) {
    mimeType = 'application/pdf';
  } else if (resolvedFilename.toLowerCase().endsWith('.docx')) {
    mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
  }

  const blob = new Blob([rawBlob], { type: mimeType });

  // 6. Create an object URL
  const downloadUrl = window.URL.createObjectURL(blob);

  // 7. Create a temporary anchor element
  const link = document.createElement('a');
  link.style.display = 'none';

  // 8. Set href to the object URL
  link.href = downloadUrl;

  // 9. Set download attribute to the appropriate filename
  link.setAttribute('download', resolvedFilename);

  // 10. Trigger the download
  document.body.appendChild(link);
  link.click();

  // 11. Remove the anchor and release the object URL safely
  document.body.removeChild(link);
  setTimeout(() => {
    window.URL.revokeObjectURL(downloadUrl);
  }, 60000);
}
