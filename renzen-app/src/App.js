import logo from './logo.svg';
import './App.css';
import { useEffect, useState } from "react"
import axios from 'axios';

function Snippet(props) {
  return (
    <div key={props.snippet.id}>
      <p>{props.snippet.title}</p>
      <p>{props.snippet.url}</p>
      <p>{props.snippet.snippet}</p>
    </div>
  )
}

function App() {

  const [response, setResponse] = useState([]);

  const fetchSnippets = async () => {

    try {
      let url = "http://localhost:81/get_snippets";
      let snippetData = await axios.post(url, {
        "login-code": document.getElementById('login-code-local').value// "0b9d0474-e020-4e54-b2c1-35d407ea796c"
      })

      setResponse(snippetData.data)
      console.log(snippetData.data)
    } catch (err) {
      console.log(err)
    }
  }

  // useEffect(() => {
  //   fetchSnippets()
  // }, [])

  return (
    <div class="container">
      <div class="col">
        <label for="login-code-local">Login Code</label>
        <input type="text" id="login-code-local" name="login-code-local"></input>
        <button onClick={() => fetchSnippets()}> Load Data</button>
      </div>
      <div class="col">
        <ul>
          {response.map(snippet => {
            return (
              <il class="list-group-item">
                <Snippet snippet={snippet} />
              </il>
            )
          }
          )}
        </ul>
      </div>
    </div>
  );
}

export default App;
