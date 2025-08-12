import React, { useEffect } from "react";

export default function Notification({ message, onClose, duration = 5000 }) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(() => {
      onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [message, onClose, duration]);

  if (!message) return null;
  return (
    <div className="notification">
      <span>{message}</span>
      <button onClick={onClose}>&times;</button>
    </div>
  );
}
