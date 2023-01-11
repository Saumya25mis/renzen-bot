import "./App.css";
import { useEffect, useState } from "react";
import { DiscordMessages } from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
import { Snippet, SnippetObject } from "./Snippet";

function App() {
  const [vscode, setVsCode] = useState<any>(null);
  const [activePage, setActivePage] = useState<string>("");
  const [gitRepo, setGitRepo] = useState<string>("");
  const [snippetResponse, setSnippetResponse] = useState<SnippetObject[]>([]);
  const [starResponse, setStarResponse] = useState<SnippetObject[]>([]);
  const [debug, setDebug] = useState<boolean>(false);
  const [visibleStarredSnippets, setVisibleStarredSnippets] = useState<Array<string>>([])
  const [visibleNonStarredSnippets, setVisibleNonStarredSnippets] = useState<Array<string>>([])

  useEffect(() => {
    // @ts-ignore
    setVsCode(acquireVsCodeApi());
    (document.getElementById('local') as HTMLInputElement).checked = true
  }, []);

  // receive messages from vs code (current active page and git repository)
  useEffect(() => {
    window.addEventListener("message", async (event) => {
      const message = event.data; // The json data that the extension sent

      if (typeof message["active_name"] !== "undefined") {
        setActivePage(message["active_name"]);
        console.log("Set activePage to: " + message["active_name"]);
      }

      if (message["git_repo"] !== "") {
        setGitRepo(message["git_repo"]);
        console.log("Set gitRepo to: " + message["git_repo"]);
      }
    });
  }, []);

  useEffect(() => {
    const buttons = document.getElementsByName(
      "bot"
    ) as NodeListOf<HTMLInputElement>;
    buttons.forEach((button) => {
      button.onclick = () => {
        fetchSnippets()
      };
    });
  }, []);

  useEffect(() => {
    fetchSnippets();
  }, [gitRepo, activePage]);

  const fetchSnippets = async () => {
    console.log("Fetching Snippets");

    let [url, login_code, prod_type] = getLoginCodesFromInputs()

    if (login_code !== "") {
      try {
        if (login_code) {
          let options: RequestInit = {
            method: "POST",
            cache: "reload",
            headers: {
              "Content-Type": "application/json;charset=utf-8",
            },
            body: JSON.stringify({
              login_code: login_code,
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
            sendMessage("Fetched: " + login_code + " " + "gitRepo");
          }
        }
      } catch (err) {
        console.log(err);
      }

    }
  };

  function getLoginCodesFromInputs(): [string, string, string] {

    let selected_checkbox = document.querySelector('input[name="bot"]:checked') as HTMLInputElement
    let corresponding_code = document.getElementById('login-code-' + selected_checkbox.id) as HTMLInputElement

    console.log([selected_checkbox.value, corresponding_code.value])

    return [selected_checkbox.value, corresponding_code.value, selected_checkbox.id]
  };

  function toggleDebugMode(): void {
    setDebug(!debug);
  };

  function sendMessage(message: string): void {
    vscode.postMessage({ type: "myMessage", value: message });
  }

  let visible_starred_snippets: Array<string> = []
  // let visible_starred_snippets: Array<string> = []

  function renderStarred() {

    // let visible_snippets: Array<string> = []
    let render_snippets: Array<any> = []

    starResponse.map((snippet_object) => {

      if (snippet_object.path === activePage) {
        visible_starred_snippets.push(snippet_object.snippet_id)

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
          />
        );
      }
    })


    // setVisibleStarredSnippets(visible_snippets)

    return render_snippets

  }

  function renderNonStarred() {

    // let non_starred_snippets: Array<any> = []
    let render_snippets: Array<any> = []

    snippetResponse.map((snippet_object) => {

      let found = visible_starred_snippets.includes(snippet_object.snippet_id)

      if (!found) {
        // non_starred_snippets.push(snippet_object.snippet_id)
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
          />
        );
      }
    })

    // setVisibleNonStarredSnippets(non_starred_snippets)

    visible_starred_snippets = []

    return render_snippets
  }


  return (
    <div className="container">
      <button
        type="button"
        className="btn btn-primary"
        onClick={toggleDebugMode}
      >
        Toggle Developer Mode
      </button>
      <div className="col">
        {debug && (
          <div>
            <div>{activePage}</div>
            <br />
            <div>{gitRepo}</div>
            {/* <br />
            Visible Starred: {visibleStarredSnippets}
            <br />
            Visible NonStarred: {visibleNonStarredSnippets} */}
          </div>
        )}
        <div className="p-3">
          <div className="container">
            <div className="border">
              <fieldset>
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

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input
                    className="form-control"
                    type="text"
                    id="login-code-production"
                    name="login-code-production"
                  />
                </div>
              </fieldset>
            </div>

            <div className="border">
              <fieldset>
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

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input
                    className="form-control"
                    type="text"
                    id="login-code-staging"
                    name="login-code-staging"
                  />
                </div>
              </fieldset>
            </div>

            <div className="border">
              <fieldset>
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

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input
                    className="form-control"
                    type="text"
                    id="login-code-local"
                    name="login-code-local"
                  />
                </div>
              </fieldset>
            </div>
          </div>
        </div>
      </div>
      <div className="col">
        STARRED TO THIS PAGE <br />
        {debug && (
          <div>
            DEBUG <br />
            {JSON.stringify(starResponse)}
          </div>
        )}
        <DiscordMessages>
          {renderStarred()}
        </DiscordMessages>
      </div>
      <div className="col">
        ALL SNIPPETS
        {debug && (
          <div>
            DEBUG <br />
            {JSON.stringify(snippetResponse)}
          </div>
        )}
        <DiscordMessages>
          {renderNonStarred()}
        </DiscordMessages>
      </div>
    </div>
  );
}

export default App;
