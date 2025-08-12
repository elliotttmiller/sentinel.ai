import { useEffect } from "react";
import { useRealtime } from "../hooks/useRealtime";
import KeyboardNavigation from "./KeyboardNavigation";

export default function SentinelInitializer() {
  useRealtime();
  useEffect(() => {
    // Any other global initialization (error handling, etc.)
  }, []);
  return <KeyboardNavigation />;
}
