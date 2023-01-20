import "./App.css";
import { useEffect, useState } from "react";
import {
  DiscordMessages,
  DiscordMessage,
  DiscordMention,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
import { SnippetStream } from "./SnippetStream";
import jwt_decode from "jwt-decode";
import {
  VSCodeTextField,
  VSCodeDropdown,
  VSCodeOption,
  VSCodeBadge,
  VSCodeButton,
  VSCodeCheckbox,
  VSCodeDataGrid,
  VSCodeDataGridCell,
  VSCodeDataGridRow,
  VSCodeDivider,
  VSCodeLink,
  VSCodePanels,
  VSCodePanelTab,
  VSCodePanelView,
  VSCodeProgressRing,
  VSCodeRadio,
  VSCodeRadioGroup,
  VSCodeTag,
  VSCodeTextArea,
} from "@vscode/webview-ui-toolkit/react";

import {
  DecodedJWt,
  ApiVersion,
  ApiProduction,
  ApiStaging,
  ApiLocal,
  SnippetObject,
  SnippetProps,
  vscode,
} from "./constants";

// import settingsImage from "./icons/settings.png";

function App() {
  // const [vscode, setVsCode] = useState<any>(null);
  const [activePage, setActivePage] = useState<string>("");
  const [gitRepo, setGitRepo] = useState<string>("");
  const [debug, setDebug] = useState<boolean>(false);
  const [githubLoginUri, setGithubLoginUri] = useState<string>("");
  const [jwt, setJwt] = useState<object>({});
  const [decodedJwt, setDecodedJwt] = useState<DecodedJWt>();
  const [apiVersion, setApiVersion] = useState<ApiVersion>(ApiLocal);

  useEffect(() => {
    // @ts-ignore
    (document.getElementById("apiDropdown") as HTMLSelectElement).value =
      "local";
    (document.getElementById("github-oauth") as HTMLAnchorElement).href = "#";
    setApiVersion(ApiLocal);
  }, []);

  // receive messages from vs code (current active page and git repository)
  useEffect(() => {
    // window.removeEventListener("message", resolveMessages)
    window.addEventListener("message", resolveMessages);

    async function resolveMessages(event: any) {
      const message = event.data; // The json data that the extension sent

      if ("URI" in message && message["URI"]) {
        const params = new URLSearchParams(message["URI"]);
        const follow_up_code = params.get("follow-up-code");
        const url =
          apiVersion.url_prefix +
          "follow-up-code?follow-up-code=" +
          follow_up_code;

        let options: RequestInit = {
          method: "POST",
          cache: "reload",
        };

        let jwt = await fetch(url, options);
        let jwt_text = await jwt.text();
        let decoded = jwt_decode(jwt_text);

        // @ts-ignore
        setJwt(jwt_text);
        // @ts-ignore
        setDecodedJwt(decoded);
      }

      if ("active_file_name" in message) {
        if (typeof message["active_file_name"] !== "undefined") {
          console.log(
            "setActivePage to " +
              message["active_file_name"] +
              " previous value: " +
              activePage
          );
          setActivePage(message["active_file_name"]);
        }
      }

      if ("git_repo" in message) {
        if (message["git_repo"] !== "") {
          console.log(
            "setGitRepo to " +
              message["git_repo"] +
              " previous value: " +
              gitRepo
          );
          setGitRepo(message["git_repo"]);
        }
      }

      if ("github_login_uri_callback" in message) {
        let github_login_uri_callback = message["github_login_uri_callback"];

        let parts = new URLSearchParams({
          dummy_hack: "dummy_hack", // when uparsing in API this gets mangled instead of needed vars
          source: "vs_code",
          source_id: "None",
          source_name: "None",
          scope: "user:email",
        });

        // API uses to open VS code (and pass one-time-code) after logging in
        let params = {
          path: github_login_uri_callback + "?" + parts.toString(),
        };

        // URL to redirect back to API
        let redirect_uri =
        apiVersion.oauth_redirect_uri +
          "?" +
          new URLSearchParams(params).toString();

        // URL used to login to github
        let url =
          "https://github.com/login/oauth/authorize?client_id=" +
          apiVersion.client_id +
          "&redirect_uri=" +
          redirect_uri;

        // final url used by HREF in login link
        console.log(
          "setGithubLoginUri to " +
            message["github_login_uri_callback"] +
            " previous value: " +
            githubLoginUri
        );
        setGithubLoginUri(url);
      }
    }
  }); //, [githubLoginUri, activePage, gitRepo]);

  useEffect(() => {
    window.onload = function () {
      vscode.postMessage({
        type: "onPageLoaded",
      });
    };
  }, []);

  useEffect(() => {
    if (githubLoginUri !== "" && gitRepo !== "") {
      (document.getElementById("github-oauth") as HTMLAnchorElement).href =
        githubLoginUri;
    } else {
      (document.getElementById("github-oauth") as HTMLAnchorElement).href = "#";
    }
  }, [githubLoginUri, gitRepo]);

  return (
    <div className="container">
      <div className="col">
        <VSCodePanels>
          <VSCodePanelTab id="tab-1">Home</VSCodePanelTab>
          <VSCodePanelTab id="tab-2">
            Settings<span> </span>
            {/* <img src={settingsImage} width="15px" height="15px" /> */}
          </VSCodePanelTab>

          <VSCodePanelView id="view-1">
            <div className="row">
              <div className="col">
                {/* For some reason 'fetch' doesn't work instead of href
                So haven't figured out how to use `VSCodeButton` for this... */}
                <a
                  id="github-oauth"
                  className="btn btn-dark"
                  role="button"
                  href={"#"}
                  // href={githubLoginUri}
                >
                  Github Oauth
                </a>
              </div>
              <div className="col">
                {!decodedJwt && (
                  <div>
                    Click on a page in your Repository, then click on the Github
                    Oauth button to begin
                  </div>
                )}
                {decodedJwt && (
                  <div>Welcome! {decodedJwt.renzen_user_name}</div>
                )}
              </div>
              <div className="col"></div>
            </div>
          </VSCodePanelView>
          <VSCodePanelView id="view-2">
            <div className="container">
              <div className="col">
                <div className="row">
                  <VSCodeButton
                    onClick={() => {
                      setDebug(!debug);
                    }}
                  >
                    Toggle Debug Mode
                  </VSCodeButton>
                  <VSCodeDivider/>
                </div>
                <div className="row">
                  <br />
                  <div className="row"><br />API Version<br /></div>
                  <br />
                  <div className="row">
                    <VSCodeDropdown id="apiDropdown">
                      <VSCodeOption
                        value={"production"}
                        onClick={() => {
                          setApiVersion(ApiProduction);
                        }}
                      >
                        Production
                      </VSCodeOption>
                      <VSCodeOption
                        value={"staging"}
                        onClick={() => {
                          setApiVersion(ApiStaging);
                        }}
                      >
                        Staging
                      </VSCodeOption>
                      <VSCodeOption
                        value={"local"}
                        onClick={() => {
                          setApiVersion(ApiLocal);
                        }}
                      >
                        Local
                      </VSCodeOption>
                    </VSCodeDropdown>
                    {/* <br />
                    <br />
                    <br />
                    <br />
                    <br />
                    <br /> */}
                    <div className="row">
                      <br />
                      <br />
                      <br />
                      <br />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </VSCodePanelView>
        </VSCodePanels>

        <br />
        <VSCodeDivider />
        <br />

        {debug && (
          <div>
            <div>{activePage}</div>
            <br />
            <div>{gitRepo}</div>
          </div>
        )}

        <SnippetStream
          activePage={activePage}
          apiVersion={apiVersion}
          gitRepo={gitRepo}
          debug={debug}
          jwt={jwt}
          decodedJwt={decodedJwt}
        />
      </div>
    </div>
  );
}

export default App;
