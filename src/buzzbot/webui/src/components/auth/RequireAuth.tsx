import { ReactNode, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const RequireAuth = ({ children }: { children: ReactNode }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const authed = typeof window !== "undefined" && localStorage.getItem("buzzbot_auth") === "1";
    if (!authed) {
      navigate("/auth", { replace: true, state: { from: location.pathname } });
    }
  }, [navigate, location]);

  const authed = typeof window !== "undefined" && localStorage.getItem("buzzbot_auth") === "1";
  if (!authed) return null;
  return <>{children}</>;
};

export default RequireAuth;
