export interface DecodedJWt {
  renzen_user_id: string;
  renzen_user_name: string;
  renzen_email: string;
}

export interface ApiVersion {
  url_prefix: string;
  name: string;
  client_id: string
  oauth_redirect_uri: string
}

export const ApiProduction: ApiVersion = {
  url_prefix: "http://production.renzen.io/",
  name: "production",
  client_id: "",
  oauth_redirect_uri: ""
};

export const ApiStaging: ApiVersion = {
  url_prefix: "http://staging.renzen.io/",
  name: "staging",
  client_id: "b18f1b8d5f29ed35f45c",
  oauth_redirect_uri: "http://staging.renzen.io/api/auth/github"
};

export const ApiLocal: ApiVersion = {
  url_prefix: "http://localhost:81/",
  name: "local",
  client_id: "b981ba10feff55da4f93",
  oauth_redirect_uri: "http://localhost:81/api/auth/github"
};

export interface SnippetObject {
  snippet_id: string;
  renzen_user_id: string;
  title: string;
  snippet: string;
  url: string;
  parsed_url: string;
  creation_timestamp: string;
  path: string;
  star_id: string;
}

export interface SnippetProps {
  snippet: SnippetObject;
  fetchSnippets: any; // function to reload snippets
  active_page: string; // current active page in vs code
  starred: boolean; // is this a starred snippet?
  fetch_url: string; // the current github repository
  debug: boolean;
  apiVersion: ApiVersion;
  jwt: any;
}

export interface SnippetStreamProps {
  activePage: string;
  apiVersion: ApiVersion;
  gitRepo: string;
  debug: boolean;
  jwt: any;
  decodedJwt: DecodedJWt | undefined;
}


// @ts-ignore
export let vscode = acquireVsCodeApi();

export function sendMessage(message: string): void {
  vscode.postMessage({ type: "myMessage", value: message });
}
