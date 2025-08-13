import { useEffect } from "react";
import ReactGA from "react-ga4";

export function useGoogleAnalytics() {
  const GA_ID = process.env.NEXT_PUBLIC_GOOGLE_ANALYTICS_TRACKING_ID;
  if (!GA_ID) return;
  useEffect(() => {
    ReactGA.initialize([{ trackingId: GA_ID }]);
  }, []);
  useEffect(() => {
    ReactGA.send({ hitType: "pageview", page: window.location.pathname });
  }, [window.location.pathname]);
}
