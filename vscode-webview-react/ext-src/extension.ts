import * as path from "path";
import * as vscode from "vscode";
import { API as BuiltInGitApi, GitExtension } from "./@types/git";

// This is ${publisher}.${name} from package.json
const extensionId = "renzen.vscode-webview-react";

export function activate(context: vscode.ExtensionContext) {
  context.subscriptions.push(
    vscode.commands.registerCommand("react-webview.start", () => {
      ReactPanel.createOrShow(context.extensionPath, context.extensionUri);
    })
  );
}

/**
 * Manages react webview panels
 */
class ReactPanel {
  /**
   * Track the currently panel. Only allow a single panel to exist at a time.
   */
  public static currentPanel: ReactPanel | undefined;

  private static readonly viewType = "react";

  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionPath: string;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];

  public static createOrShow(extensionPath: string, extensionUri: vscode.Uri) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it.
    // Otherwise, create a new panel.
    if (ReactPanel.currentPanel) {
      ReactPanel.currentPanel._panel.reveal(column);
    } else {
      ReactPanel.currentPanel = new ReactPanel(
        extensionPath,
        column || vscode.ViewColumn.One,
        extensionUri
      );
    }
  }

  private constructor(
    extensionPath: string,
    column: vscode.ViewColumn,
    extensionUri: vscode.Uri
  ) {
    this._extensionPath = extensionPath;
    this._extensionUri = extensionUri;

    // Create and show a new webview panel
    this._panel = vscode.window.createWebviewPanel(
      ReactPanel.viewType,
      "React",
      column,
      {
        // Enable javascript in the webview
        enableScripts: true,
      }
    );

    // Set the webview's initial html content
    this._panel.webview.html = this._getHtmlForWebview();

    let web_view = this._panel.webview;

    this._panel.webview.onDidReceiveMessage((data) => {
      switch (data.type) {
        case "myMessage": {
          vscode.window.showErrorMessage(data.value);
          break;
        }
        case "onPageLoaded": {
          vscode.window.onDidChangeActiveTextEditor(async (data) => {
            try {
              const extension = vscode.extensions.getExtension(
                "vscode.git"
              ) as vscode.Extension<GitExtension>;
              if (extension !== undefined && data !== undefined) {
                vscode.window.registerUriHandler({
                  handleUri(uri: vscode.Uri): vscode.ProviderResult<void> {
                    // Add your code for what to do when the authentication completes here.
                    if (uri.path === "/auth-complete") {
                      vscode.window.showInformationMessage(
                        "Sign in successful!"
                      );
                    }
                    web_view.postMessage({ URI: uri.query });
                  },
                });

                const gitExtension = extension.isActive
                  ? extension.exports
                  : await extension.activate();

                let api = gitExtension.getAPI(1);
                let fetchUrl = api.repositories[0].state.remotes[0].fetchUrl;

                const awaited_callbackUri = await vscode.env.asExternalUri(
                  vscode.Uri.parse(
                    `${vscode.env.uriScheme}://${extensionId}/auth-complete`
                  )
                );
                const callback_string = awaited_callbackUri.toString();

                console.log(callback_string);

                if (data.document?.fileName !== null) {
                  console.log("active_name: " + data.document?.fileName);
                  console.log("fetchUrl: " + fetchUrl);
                  this._panel.webview.postMessage({
                    active_name: data.document.fileName,
                    git_repo: fetchUrl,
                    callback: callback_string,
                  });
                }
              }
            } catch {
              console.log("No document or data.");
            }
          });
        }
      }
    });

    // Listen for when the panel is disposed
    // This happens when the user closes the panel or when the panel is closed programatically
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      (message) => {
        switch (message.command) {
          case "alert":
            vscode.window.showErrorMessage(message.text);
            return;
        }
      },
      null,
      this._disposables
    );
  }

  public doRefactor() {
    // Send a message to the webview webview.
    // You can send any JSON serializable data.
    this._panel.webview.postMessage({ command: "refactor" });
  }

  public dispose() {
    ReactPanel.currentPanel = undefined;

    // Clean up our resources
    this._panel.dispose();

    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  private _getHtmlForWebview() {
    const manifest = require(path.join(
      this._extensionPath,
      "build",
      "asset-manifest.json"
    ));
    const mainScript = manifest["files"]["main.js"];
    const mainStyle = manifest["files"]["main.css"];

    const scriptUri = this._panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "build", mainScript)
    );

    const styleUri = this._panel.webview.asWebviewUri(
      vscode.Uri.joinPath(this._extensionUri, "build", mainStyle)
    );

    console.log("scriptUri: " + scriptUri);

    // Use a nonce to whitelist which scripts can be run
    const nonce = getNonce();

    return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="utf-8">
				<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
				<meta name="theme-color" content="#000000">
				<title>React App</title>
				<link rel="stylesheet" type="text/css" href="${styleUri}">
				<meta http-equiv="Content-Security-Policy" content="default-src 'self' http://localhost:* localhost:* *; img-src vscode-resource: https: data:; script-src 'nonce-${nonce}';style-src 'self' vscode-resource: 'unsafe-inline' http: https: data:;">
				<base href="${this._panel.webview.asWebviewUri(
          vscode.Uri.joinPath(this._extensionUri, "build")
        )}/">
			</head>

			<body>
				<noscript>You need to enable JavaScript to run this app.</noscript>
				<div id="root"></div>

				<script nonce="${nonce}" src="${scriptUri}"></script>
			</body>
			</html>`;
  }
}

function getNonce() {
  let text = "";
  const possible =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (let i = 0; i < 32; i++) {
    text += possible.charAt(Math.floor(Math.random() * possible.length));
  }
  return text;
}
