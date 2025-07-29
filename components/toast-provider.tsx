"use client"

import { Toaster } from "react-hot-toast"
import type { ReactNode } from "react"

export function ToastProvider({ children }: { children: ReactNode }) {
  return (
    <>
      {children}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#333",
            color: "#fff",
          },
          success: {
            style: {
              background: "#166534",
              color: "white",
            },
          },
          error: {
            style: {
              background: "#7f1d1d",
              color: "white",
            },
          },
        }}
      />
    </>
  )
}