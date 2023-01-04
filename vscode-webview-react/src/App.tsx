import './App.css';
import {useState } from "react"
import axios from 'axios';

interface SnippetProps {
  id: String,
  title: String;
  url: String;
  snippet: Number;
  // handleClick: () => void;
}

const Snippet: React.FC<SnippetProps> = ({id, title, url, snippet}) => {
  return (
    <div>
      <p>{title}</p>
      <p>{url}</p>
      <p>{snippet}</p>
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
        <input type="text" id="login-code-local" name="login-code-local"></input>
        <button onClick={() => fetchSnippets()}> Load Data</button>
      </div>
      <div className="col">
        <ul>
          {response.map(snippet => {
            return (
              <div className="list-group-item">
                <Snippet id={snippet.id} title={snippet.title} url={snippet.url} snippet={snippet.snippet} />
              </div>
            )
          }
          )}
        </ul>
      </div>
    </div>
  );
}

export default App;
