import "./App.css";
import { useEffect, useState } from "react";
import {
    DiscordEmbedField,
    DiscordMessage,
    DiscordEmbed,
    DiscordEmbedFields,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";

export interface SnippetObject {
    snippet_id: string;
    renzen_user_id: string;
    title: string;
    snippet: string;
    url: string;
    parsed_url: string;
    creation_timestamp: string;
    path: string
    star_id: string
}


export interface SnippetProps {
    // from back-end
    snippet: SnippetObject
    // from front-end
    fetchSnippets: any // function to reload snippets
    active_page: string;  // current active page in vs code
    starred: boolean  // is this a starred snippet?
    fetch_url: string  // the current github repository
    debug: boolean
    getLoginCodesFromInputs: any
}

export const Snippet: React.FC<SnippetProps> = ({
    snippet,
    fetchSnippets,
    active_page,
    starred,
    fetch_url,
    debug,
    getLoginCodesFromInputs
}) => {
    const [showIframe, setShowIframe] = useState<boolean>(false);
    const [render, setRender] = useState<boolean>(true)

    function flipIframe(): void {
        setShowIframe(!showIframe);
    }

    // useEffect(() => {
    //     if (starred) {
    //         if (snippet.path !== active_page) {
    //             setRender(false)
    //         } else {
    //             setRender(true)
    //         }
    //     }
    // })

    const handleStar = async (req_type: boolean) => {

        let page_path = active_page // to star
        let [url, login_code, prod_type] = getLoginCodesFromInputs()

        if (prod_type === "local") {
            url = "http://localhost:81/star"
        } else {
            url = "http://" + prod_type + ".renzen.io/star"
        }

        let body = {
            "page_path": page_path,
            "snippet_id": snippet.snippet_id,
            "renzen_user_id": snippet.renzen_user_id,
            "req_type": req_type,
            "star_id": snippet.star_id,
            "fetch_url": fetch_url
        }

        console.log(body)

        // let url = "http://localhost:81/star";
        if (active_page) {
            let options: RequestInit = {
                method: "POST",
                cache: "reload",
                headers: {
                    "Content-Type": "application/json;charset=utf-8",
                },
                body: JSON.stringify(body),
            };
            await fetch(url, options);
            fetchSnippets()  // refresh
        }
    };


    return (
        <div>
            {render && <div className="border">
                <DiscordMessage author="renzen">
                    <DiscordEmbed
                        url={snippet.url}
                        embedTitle={snippet.parsed_url}
                        timestamp={snippet.creation_timestamp}
                    >
                        <a href={snippet.url}>{snippet.parsed_url}</a>
                        <DiscordEmbedFields slot="fields">
                            <DiscordEmbedField
                                fieldTitle={"#" + snippet.snippet_id + ": " + snippet.title}
                                inline={true}
                            >
                                {snippet.snippet}
                            </DiscordEmbedField>
                        </DiscordEmbedFields>
                        <span slot="footer">
                            <a href={snippet.url}>{snippet.url}</a>
                        </span>
                    </DiscordEmbed>
                    {!starred && <button type="button" className="btn btn-primary" onClick={() => handleStar(true)}>
                        Star To Current File
                    </button>}
                    {starred && <button type="button" className="btn btn-primary" onClick={() => handleStar(false)}>
                        Unstar From Current File
                    </button>}
                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={flipIframe}
                    >
                        Show Web Page
                    </button>
                </DiscordMessage>
                {showIframe && <iframe width={"100%"} height={"600"} src={snippet.url}></iframe>}
                <></>
                {debug && <div>
                    DEBUG <br />
                    Path: {snippet.path} <br />
                    Star ID: {snippet.star_id} <br />
                    Starred: {starred.valueOf()} <br />
                    Fetch Url: {fetch_url} <br />
                    Active Page: {active_page} <br />
                </div>}
            </div>}</div>
    );
};

export default Snippet
