import React from "react";
import { LoaderCircle } from "lucide-react";

export default function Loading({ label = "Loading data..." }) {
  return (
    <div className="state-message" role="status">
      <LoaderCircle className="spin" size={20} />
      <span>{label}</span>
    </div>
  );
}