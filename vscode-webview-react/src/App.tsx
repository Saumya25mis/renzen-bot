import "./App.css";
import { useEffect, useState } from "react";
import {
  DiscordMessages,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";
import { Snippet, SnippetProps } from "./Snippet"

function App() {
  const [vscode, setVsCode] = useState<any>(null);
  const [activePage, setActivePage] = useState<string>('');
  const [gitRepo, setGitRepo] = useState<string>('')
  const [snippetResponse, setSnippetResponse] = useState<SnippetProps[]>([]);
  const [starResponse, setStarResponse] = useState<SnippetProps[]>([]);
  // const [loginCode, setLoginCode] = useState<string>('')


  // post messages
  function sendMessage(): void {
    vscode.postMessage({ type: "myMessage", value: "MESSAGE FROM EXTENTION" });
  }

  // GET VS CODE API
  useEffect(() => {
    // @ts-ignore
    setVsCode(acquireVsCodeApi());
  }, []);

  // receive messages from vs code (current active page and git repository)
  useEffect(() => {
    window.addEventListener("message", async (event) => {
      const message = event.data; // The json data that the extension sent

      if (typeof message['active_name'] !== "undefined") {
        setActivePage(message['active_name']);
        console.log('Set activePage to: ' + message['active_name'])
      }

      if (message['git_repo'] !== '') {
        setGitRepo(message['git_repo'])
        console.log('Set gitRepo to: ' + message['git_repo'])
      }

      let login_code = document.getElementById(buttonID)//("login-code-local")
      if (login_code) {
        await fetchSnippets()
      }
    });
  }, []);


  const [loginCodes, setloginCodes] = useState<Record<string, string>>({})

  // get all login codes from elements
  const setFetchValues = () => {

    setloginCodes({
      'login-code-local': (document.getElementById('login-code-local') as HTMLInputElement).value,
      'login-code-staging': (document.getElementById('login-code-staging') as HTMLInputElement).value,
      'login-code-production': (document.getElementById('login-code-production') as HTMLInputElement).value,
    })
    fetchSnippets()

  }

  const [botPath, setBotPath] = useState<string>("")
  const [buttonID, setButtonID] = useState<string>("")

  // add onClick to version selectors (prod, staging, local)
  // onClick, set as current version
  useEffect(() => {
    const buttons = document.getElementsByName("bot") as NodeListOf<HTMLInputElement>
    buttons.forEach(button => {
      button.onclick = () => {
        if (button.checked) {
          // alert(button.value + " selected as contact option!");
          let selected = document.querySelector('input[name="bot"]:checked')
          let bot_path = button.value
          let button_id = button.id
          setBotPath(bot_path)  // url
          setButtonID('login-code-' + button_id) // selected bot button
        }
      }
    })
  }, [])

  const fetchSnippets = async () => {
    console.log("Fetching Snippets")

    let login_code = loginCodes[buttonID]

    try {
      let url = botPath  //"http://localhost:81/get_snippets";
      if (login_code) {
let options: RequestInit = {
  method: "POST",
  cache: "reload",
  headers: {
    "Content-Type": "application/json;charset=utf-8",
  },
  body: JSON.stringify({
    "login_code": login_code,
    "fetch_url": gitRepo
  }),
};
        console.log(options)
        let snippetData = await fetch(url, options);
        let data = await snippetData.json();
        setSnippetResponse(data['all_dicts']);
        setStarResponse(data['starred_dicts'])
        console.log(data);
      }
    } catch (err) {
      console.log(err);
    }
  };

  const [debug, setDebug] = useState<boolean>(false)
  const toggleDebug = () => {
    setDebug(!debug)
  }

  return (
    <div className="container">
      <button
        type="button"
        className="btn btn-primary"
        onClick={toggleDebug}
      >
        Toggle Developer Mode
      </button>
      <div className="col">
        {debug && <div>
          <div>{activePage}</div>
          <br />
          <div>{gitRepo}</div>
        </div>}
        <div className="p-3">
          <div className="container">

            <div className="border">
              <fieldset>

                <div className="input-group input-group-sm mb-3 justify-content-center">
                  <div className="input-group-text">
                    <input className="form-check-input mt-0" type="radio" id="production" name="bot"
                      value="http://production.renzen.io/get_snippets" />
                  </div>
                  <div className="input-group-text">Production</div>
                </div>

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input className="form-control" type="text" id="login-code-production"
                    name="login-code-production" />
                </div>

              </fieldset>
            </div>


            <div className="border">
              <fieldset>

                <div className="input-group input-group-sm mb-3 justify-content-center">
                  <div className="input-group-text">
                    <input className="form-check-input mt-0" type="radio" id="staging" name="bot"
                      value="http://staging.renzen.io/get_snippets" />
                  </div>
                  <div className="input-group-text">Staging</div>
                </div>

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input className="form-control" type="text" id="login-code-staging" name="login-code-staging" />
                </div>

              </fieldset>
            </div>

            <div className="border">
              <fieldset>

                <div className="input-group input-group-sm mb-3 justify-content-center">
                  <div className="input-group-text">
                    <input className="form-check-input" type="radio" id="local" name="bot"
                      value="http://localhost:81/get_snippets" />
                  </div>
                  <div className="input-group-text">Local</div>
                </div>

                <div className="input-group input-group-sm mb-3">
                  <span className="input-group-text">Login Code</span>
                  <input className="form-control" type="text" id="login-code-local" name="login-code-local" defaultValue={'b1b86505-a6ca-41fb-8627-dc4679179958'} />
                </div>

              </fieldset>
            </div>

            <div className="row">
              <button className="btn btn-primary" id="login-btn" onClick={setFetchValues}>Login All</button>
            </div>

          </div>
        </div>
        {/* <br />
        <button onClick={sendMessage} className="btn btn-primary">Send Message to Extension</button>
        <br />
        <label htmlFor="login-code-local">Login Code</label>
        <input
          type="text"
          id="login-code-local"
          name="login-code-local"
          defaultValue={"278aba8a-aae3-42c6-95c1-5a0eaa55aec9"}
        ></input>
        <button className="btn btn-primary" onClick={() => Login()}>Fetch Data</button> */}
      </div>
      <div className="col">
        STARRED TO THIS PAGE <br />
        {debug && <div>
          DEBUG <br />
          {JSON.stringify(starResponse)}
        </div>}
        <DiscordMessages>
          <ul>
            {starResponse.map((snippet) => {
              return (
                <div className="list-group-item">
                  <Snippet
                    key={snippet.star_id}
                    active_page={activePage}
                    snippet_id={snippet.snippet_id}
                    title={snippet.title}
                    url={snippet.url}
                    parsed_url={snippet.parsed_url}
                    snippet={snippet.snippet}
                    creation_timestamp={snippet.creation_timestamp}
                    starred={true}
                    path={snippet.path}
                    fetchSnippets={fetchSnippets}
                    renzen_user_id={snippet.renzen_user_id}
                    star_id={snippet.star_id}
                    fetch_url={gitRepo}
                    debug={debug}
                  />
                </div>
              );
            })}
          </ul>
        </DiscordMessages>
      </div>
      <div className="col">
        ALL SNIPPETS
        {debug && <div>
          DEBUG <br />
          {JSON.stringify(snippetResponse)}
        </div>}
        <DiscordMessages>
          <ul>
            {snippetResponse.map((snippet) => {
              return (
                <div className="list-group-item">
                  <Snippet
                    key={snippet.snippet_id}
                    active_page={activePage}
                    snippet_id={snippet.snippet_id}
                    title={snippet.title}
                    url={snippet.url}
                    parsed_url={snippet.parsed_url}
                    snippet={snippet.snippet}
                    creation_timestamp={snippet.creation_timestamp}
                    path={snippet.path}
                    starred={false}
                    fetchSnippets={fetchSnippets}
                    renzen_user_id={snippet.renzen_user_id}
                    star_id={""}
                    fetch_url={gitRepo}
                    debug={debug}
                  />
                </div>
              );
            })}
          </ul>
        </DiscordMessages>
      </div>
    </div>
  );
}

export default App;
