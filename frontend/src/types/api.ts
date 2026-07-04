/**
 * API-level types: error response shape and typed exception.
 * Mirrors API.md §5.6 and §6.
 */

export interface ApiError {
  detail: string;
  code?: string;
}

export class ApiException extends Error {
  constructor(
    public readonly error: ApiError,
    public readonly status: number,
  ) {
    super(error.detail);
    this.name = "ApiException";
  }

  get code(): string | undefined {
    return this.error.code;
  }
}
