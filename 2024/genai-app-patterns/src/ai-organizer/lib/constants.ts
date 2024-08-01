export const ROOT_ROUTE = '/signin';
export const HOME_ROUTE = '/';

export const SESSION_COOKIE_NAME = 'user_session';
export const APPLICATION_NAME = 'AI organizer';

export const MAX_FILE_SIZE = {
  'application/pdf': 30 * 1024 * 1024, // https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/document-understanding#supported_models
  'text/html': 10 * 1024 * 1024,
  'text/json': 1 * 1024 * 1024,
  'text/markdown': 10 * 1024 * 1024,
  'text/plain': 10 * 1024 * 1024,
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 10 * 1024 * 1024,
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 10 * 1024 * 1024
};
