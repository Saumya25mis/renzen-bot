import "./App.css";
import { useEffect, useState } from "react";
import {
  DiscordMessages,
  DiscordMessage,
  DiscordMention,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
import { Snippet } from "./Snippet";
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
  GITHUB_LOCAL_OAUTH_CLIENT_ID,
  GITHUB_LOCAL_OAUTH_REDIRECT_URI,
  SnippetStreamProps,
  sendMessage,
} from "./constants";

export const SnippetStream: React.FC<SnippetStreamProps> = ({
  activePage,
  apiVersion,
  gitRepo,
  debug,
  jwt,
  decodedJwt,
}) => {
  const [showAsStarred, setShowAsStarred] = useState<SnippetObject[]>([]);
  const [dontShowAsStarred, setDontShowAsStarred] = useState<SnippetObject[]>(
    []
  );

  useEffect(() => {
    fetchSnippets();
  }, [activePage, apiVersion, gitRepo, jwt, decodedJwt, debug]);

  const fetchSnippets = async () => {
    console.log("Fetching Snippets");
    console.log(apiVersion.url_prefix);

    let url = apiVersion.url_prefix + "get_snippets";

    console.log("Git repo in fetch: " + gitRepo);

    if (gitRepo !== "" && decodedJwt !== undefined) {
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
        let snippet_response: SnippetObject[] = data["all_dicts"];
        let star_response: SnippetObject[] = data["starred_dicts"];

        let visible_starred_snippets: Array<string> = [];

        let render_snippets: Array<any> = [];

        star_response.map((snippet_object) => {
          if (snippet_object.path === activePage) {
            visible_starred_snippets.push(snippet_object.snippet_id);

            render_snippets.push(
              <Snippet
                key={snippet_object.star_id}
                active_page={activePage}
                snippet={snippet_object}
                starred={true}
                fetchSnippets={fetchSnippets}
                apiVersion={apiVersion}
                fetch_url={gitRepo}
                debug={debug}
                jwt={jwt}
              />
            );
          }
        });

        setShowAsStarred(render_snippets);

        render_snippets = [];

        snippet_response.map((snippet_object) => {
          let found = visible_starred_snippets.includes(
            snippet_object.snippet_id
          );

          if (!found) {
            render_snippets.push(
              <Snippet
                key={snippet_object.snippet_id}
                active_page={activePage}
                snippet={snippet_object}
                starred={false}
                apiVersion={apiVersion}
                fetchSnippets={fetchSnippets}
                fetch_url={gitRepo}
                debug={debug}
                jwt={jwt}
              />
            );
          }
        });

        setDontShowAsStarred(render_snippets);
      } catch (err) {
        console.log(err);
      }
    }
  };

  return (
    <div className="col">
      <DiscordMessages author="Starred To Page">
        {showAsStarred}
      </DiscordMessages>
      <br />
      <DiscordMessages author="All Snippets">
        {dontShowAsStarred}
      </DiscordMessages>
    </div>
  );
};
