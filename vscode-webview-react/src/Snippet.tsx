import "./App.css";
import { useEffect, useState } from "react";
import {
    DiscordEmbedField,
    DiscordMessage,
    DiscordEmbed,
    DiscordEmbedFields,
} from "@danktuary/react-discord-message";
import "bootstrap/dist/css/bootstrap.min.css";


export interface SnippetProps {
    // from back-end
    snippet_id: string;
    renzen_user_id: string;
    title: string;
    snippet: string;
    url: string;
    parsed_url: string;
    creation_timestamp: string;
    path: string
    star_id: string
    // from front-end
    fetchSnippets: any // function to reload snippets
    active_page: string;  // current active page in vs code
    starred: boolean  // is this a starred snippet?
    fetch_url: string  // the current github repository
    debug: boolean
}

export const Snippet: React.FC<SnippetProps> = ({
    snippet_id,
    renzen_user_id,
    title,
    snippet,
    url,
    parsed_url,
    creation_timestamp,
    path,
    star_id,
    fetchSnippets,
    active_page,
    starred,
    fetch_url,
    debug
}) => {
    const [showIframe, setShowIframe] = useState<boolean>(false);
    const [render, setRender] = useState<boolean>(true)

    function flipIframe(): void {
        setShowIframe(!showIframe);
    }

    useEffect(() => {
        if (starred) {
            if (path !== active_page) {
                setRender(false)
            } else {
                setRender(true)
            }
        }
    })

    const handleStar = async (req_type: boolean) => {

        let page_path = active_page // to star

        if (!req_type) {
            // unstar
            let page_path = path // set to snippet page
        }

        let body = {
            "page_path": page_path,
            "snippet_id": snippet_id,
            "renzen_user_id": renzen_user_id,
            "req_type": req_type,
            "star_id": star_id,
            "fetch_url": fetch_url
        }

        console.log(body)

        let url = "http://localhost:81/star";
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
                        url={url}
                        embedTitle={parsed_url}
                        timestamp={creation_timestamp}
                    >
                        <a href={url}>{parsed_url}</a>
                        <DiscordEmbedFields slot="fields">
                            <DiscordEmbedField
                                fieldTitle={"#" + snippet_id + ": " + title}
                                inline={true}
                            >
                                {snippet}
                            </DiscordEmbedField>
                        </DiscordEmbedFields>
                        <span slot="footer">
                            <a href={url}>{url}</a>
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
                {showIframe && <iframe width={"100%"} height={"600"} src={url}></iframe>}
                <></>
                {debug && <div>
                    DEBUG <br />
                    Path: {path} <br />
                    Star ID: {star_id} <br />
                    Starred: {starred.valueOf()} <br />
                    Fetch Url: {fetch_url} <br />
                    Active Page: {active_page} <br />
                </div>}
            </div>}</div>
    );
};

export default Snippet
