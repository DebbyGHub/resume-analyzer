import { useRef, useState, type DragEvent, type ChangeEvent } from "react";

interface UploadBoxProps {
  file: File | null;
  onFileSelect: (file: File) => void;
  error?: string;
}

export function UploadBox({ file, onFileSelect, error }: UploadBoxProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function validateAndSelect(candidate: File) {
    if (candidate.type !== "application/pdf") {
      return; // parent validation handles error display
    }
    onFileSelect(candidate);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) validateAndSelect(dropped);
  }

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const picked = e.target.files?.[0];
    if (picked) validateAndSelect(picked);
  }

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Upload resume PDF"
      onClick={() => inputRef.current?.click()}
      onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={
        "relative flex flex-col items-center justify-center gap-3 " +
        "rounded-xl border-2 border-dashed p-10 cursor-pointer " +
        "transition-all duration-200 " +
        (dragging
          ? "drag-active border-accent"
          : error
            ? "border-score-low bg-score-low/5"
            : file
              ? "border-score-high/50 bg-score-high/5"
              : "border-surface-border hover:border-text-muted hover:bg-surface-raised")
      }
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="sr-only"
        onChange={handleChange}
        tabIndex={-1}
      />

      {/* Icon */}
      <div
        className={
          "flex h-12 w-12 items-center justify-center rounded-full " +
          (file ? "bg-score-high/10" : "bg-surface-border/60")
        }
      >
        {file ? (
          <svg
            className="h-6 w-6 text-score-high"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        ) : (
          <svg
            className="h-6 w-6 text-text-muted"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m6.75 12l-3-3m0 0l-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
            />
          </svg>
        )}
      </div>

      {/* Text */}
      {file ? (
        <div className="text-center">
          <p className="text-sm font-medium text-score-high font-display">
            {file.name}
          </p>
          <p className="text-xs text-text-muted mt-0.5">
            {(file.size / 1024).toFixed(0)} KB · Click to replace
          </p>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-sm font-medium text-text-primary font-display">
            Drop your resume here
          </p>
          <p className="text-xs text-text-muted mt-0.5">
            PDF only · or click to browse
          </p>
        </div>
      )}

      {error && (
        <p className="absolute -bottom-6 left-0 text-xs text-score-low">
          {error}
        </p>
      )}
    </div>
  );
}
