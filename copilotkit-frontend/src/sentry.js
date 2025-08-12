import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN || "https://bab9b47561dd7ee4f5d1db13fda02c37@o4509683080822784.ingest.us.sentry.io/4509764514938880",
  integrations: [new Sentry.BrowserTracing()],
  tracesSampleRate: 1.0,
});

window.Sentry = Sentry;
