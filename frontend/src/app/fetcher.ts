import wretch, { Wretch, WretchError } from "wretch";
import { AuthActions } from "@/app/auth/utils";

const { handleJWTRefresh, storeToken, getToken } = AuthActions();

const api = () => {
  return (
    wretch(`${process.env.NEXT_PUBLIC_API_BASE_URL}`)
      .headers({
        // "Access-Control-Allow-Origin": "http://localhost:3000",
        "Content-Type": "application/json",
      })
      .auth(`Bearer ${getToken("access")}`)
      .catcher(401, async (error: WretchError, request: Wretch) => {
        try {
          const { access } = (await handleJWTRefresh().json()) as {
            access: string;
          };

          storeToken(access, "access");

          return request
            .auth(`Bearer ${access}`)
            .fetch()
            .unauthorized(() => {
              window.location.replace("/");
            })
            .json();
        } catch (err) {
          window.location.replace("/");
        }
      })
  );
};

export const fetcher = (url: string): Promise<any> => {
  return api().get(url).json();
};

export const postFetcher = (url: string, body: any): Promise<any> => {
  return api().url(url).post(body).json();
};
