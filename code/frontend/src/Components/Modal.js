import React from "react";
import "../CSS/Modal.css";

// Base layout for modals as we use a few
export default function Modal({ open, title, onClose, children, footer }) {
  if (!open) return null;

  return (
    <div className="modalOverlay" onMouseDown={onClose}>
      <div className="modalCard" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modalHeader">
          <h3>{title}</h3>
          <button className="modalClose" onClick={onClose} aria-label="Close"> x</button>
        </div>
        <div className="modalBody">{children}</div>
        {footer && <div className="modalFooter">{footer}</div>}
      </div>
    </div>
  );
}