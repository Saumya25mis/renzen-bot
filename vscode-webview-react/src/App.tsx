import './App.css';
import {useState } from "react"
import axios from 'axios';
import {DiscordEmbedField, DiscordMessage, DiscordMessages, DiscordEmbed, DiscordEmbedFields  } from '@danktuary/react-discord-message'
import 'bootstrap/dist/css/bootstrap.min.css';

interface SnippetProps {
  snippet_id: string,
  title: string;
  parsed_url: string
  url: string;
  snippet: string;
  creation_timestamp: string
  // handleClick: () => void;
}

const Snippet: React.FC<SnippetProps> = ({snippet_id, title, url, snippet, creation_timestamp, parsed_url}) => {
  return (
    <div className="border">
      <DiscordMessage author="renzen">
        <DiscordEmbed
          url={url} embedTitle={parsed_url} timestamp={creation_timestamp}>
            <a href={url}>{parsed_url}</a>
          <DiscordEmbedFields slot="fields">
            <DiscordEmbedField fieldTitle={"#"+snippet_id+": "+title} inline={true}>
              {snippet}
            </DiscordEmbedField>
          </DiscordEmbedFields>
          <span slot="footer"><a href={url}>{url}</a></span>
        </DiscordEmbed>
        <button type="button" className="btn btn-primary">Star To Current File</button>
        <button type="button" className="btn btn-primary">Show Web Page</button>
      </DiscordMessage>
    </div>
  )
}



function App() {

  const [response, setResponse] = useState<SnippetProps[]>([]);

  console.log("Test")

  const fetchSnippets = async () => {

    console.log("Test")

    try {
      let url = "http://localhost:81/get_snippets";
      let login_code = document.getElementById('login-code-local')
      if (login_code) {
        let options: RequestInit = {
          'method': 'POST',
          'cache': 'reload',
          'headers': {
            'Content-Type': 'application/json;charset=utf-8'
          },
          'body': JSON.stringify({"login-code": (login_code as HTMLInputElement).value})
        }
        let snippetData = await fetch(url, options)
        let data = await snippetData.json()
        setResponse(data)
        console.log(data)
      }

    } catch (err) {
      console.log(err)
    }
  }

  return (
    <div className="container">
      <div className="col">
        <label htmlFor="login-code-local">Login Code</label>
        <input type="text" id="login-code-local" name="login-code-local" defaultValue={"4827c4c8-1416-4d74-8771-1c18a6bfeea4"}></input>
        <button onClick={() => fetchSnippets()}> Load Data</button>
      </div>
      <div className="col">
        <DiscordMessages>
        <ul>
          {response.map(snippet => {
            return (
              <div className="list-group-item">
                <Snippet snippet_id={snippet.snippet_id} title={snippet.title} url={snippet.url} snippet={snippet.snippet} creation_timestamp={snippet.creation_timestamp} parsed_url={snippet.parsed_url}/>
              </div>
            )
          }
          )}
        </ul>
        </DiscordMessages>
      </div>
    </div>
  );
}

export default App;
