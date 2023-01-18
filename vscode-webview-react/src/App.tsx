import "./App.css";
import { useEffect, useState } from "react";
import {
  DiscordMessages,
  DiscordMessage,
  DiscordMention,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
import { Snippet, SnippetObject } from "./Snippet";
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

import settingsImage from "./icons/settings.png";

// @ts-ignore
let vscode = acquireVsCodeApi();

const GITHUB_LOCAL_OAUTH_CLIENT_ID = "b981ba10feff55da4f93";
const GITHUB_LOCAL_OAUTH_REDIRECT_URI = "http://localhost:81/api/auth/github";

function App() {
  // const [vscode, setVsCode] = useState<any>(null);
  const [activePage, setActivePage] = useState<string>("");
  const [gitRepo, setGitRepo] = useState<string>("");
  const [snippetResponse, setSnippetResponse] = useState<SnippetObject[]>([]);
  const [starResponse, setStarResponse] = useState<SnippetObject[]>([]);
  const [debug, setDebug] = useState<boolean>(false);
  const [callbackUri, setCallbackUri] = useState<string>("");
  const [UriData, setUriData] = useState<string>("");
  const [jwt, setJwt] = useState<object>({});
  const [decodedJwt, setDecodedJwt] = useState<object>({});

  useEffect(() => {
    // @ts-ignore
    (document.getElementById("local") as HTMLInputElement).checked = true;
  }, []);

  // receive messages from vs code (current active page and git repository)
  useEffect(() => {
    window.addEventListener("message", async (event) => {
      const message = event.data; // The json data that the extension sent

      if ("URI" in message) {
        console.log("found uri data.");

        const params = new URLSearchParams(message["URI"]);
        const follow_up_code = params.get("follow-up-code");
        console.log("follow up code: " + follow_up_code);
        const url =
          "http://localhost:81/follow-up-code?follow-up-code=" + follow_up_code;
        console.log("url: " + url);

        let options: RequestInit = {
          method: "POST",
          cache: "reload",
        };

        let jwt = await fetch(url, options);
        console.log("fetched");
        let jwt_text = await jwt.text();

        console.log("jwt text: " + jwt_text);
        var decoded = jwt_decode(jwt_text);
        console.log("decoded: " + JSON.stringify(decoded));
        // @ts-ignore
        setJwt(jwt_text);
        // @ts-ignore
        setDecodedJwt(decoded);

        setUriData(message["URI"]);
      }

      if ("active_name" in message) {
        if (typeof message["active_name"] !== "undefined") {
          setActivePage(message["active_name"]);
          console.log("Set activePage to: " + message["active_name"]);
        }
      }

      if ("git_repo" in message) {
        if (message["git_repo"] !== "") {
          setGitRepo(message["git_repo"]);
          console.log("Set gitRepo to: " + message["git_repo"]);
        }
      }

      if ("callback" in message) {
        let callback_string = message["callback"];
        console.log(callback_string);

        let source = "vs_code";
        let source_id = "None";
        let source_name = "None";

        let parts = new URLSearchParams({
          dummy_hack: "dummy_hack", // when uparsing in API this gets mangled instead of needed vars
          source: source,
          source_id: source_id,
          source_name: source_name,
          scope: "user:email",
        });

        let params = {
          path: callback_string + "?" + parts.toString(),
        };

        let redirect_uri =
          GITHUB_LOCAL_OAUTH_REDIRECT_URI +
          "?" +
          new URLSearchParams(params).toString();

        let url =
          "https://github.com/login/oauth/authorize?client_id=" +
          GITHUB_LOCAL_OAUTH_CLIENT_ID +
          "&redirect_uri=" +
          redirect_uri;

        setCallbackUri(url);
      }
    });
  }, []);

  useEffect(() => {
    const buttons = document.getElementsByName(
      "bot"
    ) as NodeListOf<HTMLInputElement>;
    buttons.forEach((button) => {
      button.onclick = () => {
        fetchSnippets();
      };
    });
  }, []);

  useEffect(() => {
    fetchSnippets();
  }, [gitRepo, activePage, jwt, UriData, decodedJwt, callbackUri]);

  const fetchSnippets = async () => {
    console.log("Fetching Snippets");

    let [url, login_code, prod_type] = getLoginCodesFromInputs();

    console.log("Git repo in fetch: " + gitRepo);

    if (gitRepo !== "" && Object.keys(jwt).length !== 0) {
      try {
        let options: RequestInit = {
          method: "POST",
          cache: "reload",
          headers: {
            "Content-Type": "application/json;charset=utf-8",
            Authorization: "Bearer " + jwt.toString(),
          },
          body: JSON.stringify({
            fetch_url: gitRepo,
          }),
        };
        console.log(options);
        let snippetData = await fetch(url, options);
        let data = await snippetData.json();
        setSnippetResponse(data["all_dicts"]);
        setStarResponse(data["starred_dicts"]);
        console.log(data);
        if (debug) {
          sendMessage("Fetched: " + " " + "gitRepo");
        }
      } catch (err) {
        console.log(err);
      }
    }
  };

  useEffect(() => {
    window.onload = function () {
      vscode.postMessage({
        type: "onPageLoaded",
      });
    };
  }, []);

  function getLoginCodesFromInputs(): [string, string, string] {
    let selected_checkbox = document.querySelector(
      'input[name="bot"]:checked'
    ) as HTMLInputElement;
    console.log([selected_checkbox.value, ""]);
    return [selected_checkbox.value, "", selected_checkbox.id];
  }

  function toggleDebugMode(): void {
    setDebug(!debug);
  }

  function sendMessage(message: string): void {
    vscode.postMessage({ type: "myMessage", value: message });
  }

  let visible_starred_snippets: Array<string> = [];

  function renderStarred() {
    let render_snippets: Array<any> = [];

    starResponse.map((snippet_object) => {
      if (snippet_object.path === activePage) {
        visible_starred_snippets.push(snippet_object.snippet_id);

        render_snippets.push(
          <Snippet
            key={snippet_object.star_id}
            active_page={activePage}
            snippet={snippet_object}
            starred={true}
            fetchSnippets={fetchSnippets}
            getLoginCodesFromInputs={getLoginCodesFromInputs}
            fetch_url={gitRepo}
            debug={debug}
            jwt={jwt}
          />
        );
      }
    });

    return (
      <DiscordMessage author="Starred Snippets">
        {render_snippets}
      </DiscordMessage>
    );
  }

  function renderNonStarred() {
    let render_snippets: Array<any> = [];

    snippetResponse.map((snippet_object) => {
      let found = visible_starred_snippets.includes(snippet_object.snippet_id);

      if (!found) {
        render_snippets.push(
          <Snippet
            key={snippet_object.snippet_id}
            active_page={activePage}
            snippet={snippet_object}
            starred={false}
            getLoginCodesFromInputs={getLoginCodesFromInputs}
            fetchSnippets={fetchSnippets}
            fetch_url={gitRepo}
            debug={debug}
            jwt={jwt}
          />
        );
      }
    });

    visible_starred_snippets = [];

    return (
      <DiscordMessage author="All Snippets">{render_snippets}</DiscordMessage>
    );
  }

  return (
    <div className="container">
      <VSCodePanels>
        <VSCodePanelTab id="tab-1">Home</VSCodePanelTab>
        <VSCodePanelTab id="tab-2">
          Settings
          <img src={settingsImage} width="15px" height="15px" />
        </VSCodePanelTab>

        <VSCodePanelView id="view-1">
          {callbackUri !== "" && (
            <a className="btn btn-info" role="button" href={callbackUri}>
              Github Oauth
            </a>
          )}
        </VSCodePanelView>
        <VSCodePanelView id="view-2">
          <button
            type="button"
            className="btn btn-primary"
            onClick={toggleDebugMode}
          >
            Toggle Developer Mode
          </button>
          <div>API Version</div>
          <div className="input-group input-group-sm mb-3 justify-content-center">
            <div className="input-group-text">
              <input
                className="form-check-input"
                type="radio"
                id="local"
                name="bot"
                value="http://localhost:81/get_snippets"
              />
            </div>
            <div className="input-group-text">Local</div>
          </div>
          <div className="input-group input-group-sm mb-3 justify-content-center">
            <div className="input-group-text">
              <input
                className="form-check-input mt-0"
                type="radio"
                id="staging"
                name="bot"
                value="http://staging.renzen.io/get_snippets"
              />
            </div>
            <div className="input-group-text">Staging</div>
          </div>
          <div className="input-group input-group-sm mb-3 justify-content-center">
            <div className="input-group-text">
              <input
                className="form-check-input mt-0"
                type="radio"
                id="production"
                name="bot"
                value="http://production.renzen.io/get_snippets"
              />
            </div>
            <div className="input-group-text">Production</div>
          </div>
        </VSCodePanelView>
      </VSCodePanels>

      <div className="col">
        {debug && (
          <div>
            <div>{activePage}</div>
            <br />
            <div>{gitRepo}</div>
          </div>
        )}
        <div className="p-3">
          <div className="container">
            <div className="border">
              <VSCodeDropdown>
                <VSCodeOption>Option Label #1</VSCodeOption>
                <VSCodeOption>Option Label #2</VSCodeOption>
                <VSCodeOption>Option Label #3</VSCodeOption>
              </VSCodeDropdown>

              <VSCodeTextField value={"hi"} />
            </div>
          </div>
        </div>
      </div>
      <div className="col">
        {debug && (
          <div>
            DEBUG <br />
            {JSON.stringify(starResponse)}
          </div>
        )}
        <DiscordMessages>{renderStarred()}</DiscordMessages>
      </div>
      <div className="col">
        <br />
        {debug && (
          <div>
            DEBUG <br />
            {JSON.stringify(snippetResponse)}
          </div>
        )}
        <DiscordMessages>{renderNonStarred()}</DiscordMessages>
      </div>
    </div>
  );
}

export default App;
