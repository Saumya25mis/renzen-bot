import "./App.css";
import { useEffect, useState } from "react";
import {
  DiscordEmbedField,
  DiscordMessage,
  DiscordEmbed,
  DiscordEmbedFields,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
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

export const Snippet: React.FC<SnippetProps> = ({
  snippet,
  fetchSnippets,
  active_page,
  starred,
  fetch_url,
  debug,
  apiVersion,
  jwt,
}) => {
  const handleStar = async (req_type: boolean) => {
    let page_path = active_page; // to star

    let url = apiVersion.url_prefix + "star";

    let body = {
      page_path: page_path,
      snippet_id: snippet.snippet_id,
      renzen_user_id: snippet.renzen_user_id,
      req_type: req_type,
      star_id: snippet.star_id,
      fetch_url: fetch_url,
    };

    if (active_page) {
      let options: RequestInit = {
        method: "POST",
        cache: "reload",
        headers: {
          "Content-Type": "application/json;charset=utf-8",
          Authorization: "Bearer " + jwt,
        },
        body: JSON.stringify(body),
      };
      await fetch(url, options);
      fetchSnippets();
    }
  };

  return (
    <div>
        <DiscordEmbed
          url={snippet.url}
          embedTitle={snippet.parsed_url}
          timestamp={snippet.creation_timestamp}
          slot="embeds"
        >
          <a href={snippet.url}>{snippet.parsed_url}</a>
          <DiscordEmbedFields slot="fields">
            <DiscordEmbedField
              fieldTitle={snippet.title}
              // inline={true}
            >
              {snippet.snippet}
            </DiscordEmbedField>
          </DiscordEmbedFields>
          <span slot="footer">
            <a href={snippet.url}>{snippet.url}</a>
          </span>
        </DiscordEmbed>
        {!starred && (
          <VSCodeButton onClick={() => handleStar(true)}>
            Star To Current File
          </VSCodeButton>
        )}
        {starred && (
          <VSCodeButton onClick={() => handleStar(false)}>
            Unstar From Current File
          </VSCodeButton>
        )}
        {debug && (
          <div>
            DEBUG <br />
            Path: {snippet.path} <br />
            Star ID: {snippet.star_id} <br />
            Starred: {starred.valueOf()} <br />
            Fetch Url: {fetch_url} <br />
            Active Page: {active_page} <br />
          </div>
        )}
    </div>
  );
};

export default Snippet;
