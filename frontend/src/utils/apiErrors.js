export function getApiErrorMessage(error) {
  const status = error.response?.status;
  const detail = error.response?.data?.detail;

  if (status === 400) {
    return typeof detail === "string"
      ? detail
      : "The request could not be processed.";
  }

  if (status === 401) {
    return "Your session has expired. Please sign in again.";
  }

  if (status === 403) {
    return "You do not have permission to perform this action.";
  }

  if (status === 404) {
    return "The requested resource was not found.";
  }

  if (status === 413) {
    return "The uploaded file exceeds the permitted size.";
  }

  if (status === 422) {
    return typeof detail === "string"
      ? detail
      : "Some fields are invalid. Check your input and try again.";
  }

  if (status === 429) {
    return "Too many requests. Please wait and try again.";
  }

  if (status >= 500) {
    return "The server encountered an error. Please try again later.";
  }

  if (!error.response) {
    return "Cannot connect to the server. Check your connection and try again.";
  }

  return "Something went wrong. Please try again.";
}