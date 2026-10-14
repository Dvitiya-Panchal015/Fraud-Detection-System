import React from "react";
import { AlertCircle } from "lucide-react";

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-state" role="alert">
      <AlertCircle size={19} />
      <div>
        <strong>Could not load this section</strong>
        <p>{message}</p>
        {onRetry && (
          <button className="text-button" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    </div>
  );
}