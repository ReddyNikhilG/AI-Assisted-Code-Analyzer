const vscode = require('vscode');
const { analyzeCode, checkHealth } = require('./analyzer');
const { createDiagnostics, getHoverInfo } = require('./diagnostics');

/** @type {vscode.DiagnosticCollection} */
let diagnosticCollection;

/** @type {vscode.StatusBarItem} */
let statusBarItem;

/** @type {NodeJS.Timeout|null} */
let debounceTimer = null;

/** Cached analysis result for hover provider */
let lastResult = null;
let lastDocUri = null;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('CodeSense AI extension activated');

    // Create diagnostic collection
    diagnosticCollection = vscode.languages.createDiagnosticCollection('codesense');
    context.subscriptions.push(diagnosticCollection);

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusBarItem.command = 'codesense.analyzeFile';
    statusBarItem.text = '$(shield) CodeSense';
    statusBarItem.tooltip = 'Click to analyze current file';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('codesense.analyzeFile', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'python') {
                runAnalysis(editor.document);
            } else {
                vscode.window.showInformationMessage('CodeSense: Open a Python file to analyze.');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('codesense.showDashboard', () => {
            const config = vscode.workspace.getConfiguration('codesense');
            const backendUrl = config.get('backendUrl', 'http://127.0.0.1:8000');
            vscode.env.openExternal(vscode.Uri.parse(backendUrl));
        })
    );

    // Register hover provider for Python
    context.subscriptions.push(
        vscode.languages.registerHoverProvider('python', {
            provideHover(document, position) {
                if (!lastResult || !lastDocUri || lastDocUri !== document.uri.toString()) {
                    return null;
                }
                const hover = getHoverInfo(lastResult, position);
                if (hover) {
                    return new vscode.Hover(hover);
                }
                return null;
            }
        })
    );

    // Analyze on save
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((document) => {
            const config = vscode.workspace.getConfiguration('codesense');
            if (config.get('analyzeOnSave', true) && document.languageId === 'python') {
                runAnalysis(document);
            }
        })
    );

    // Analyze on type (debounced)
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument((event) => {
            const config = vscode.workspace.getConfiguration('codesense');
            if (config.get('analyzeOnType', false) && event.document.languageId === 'python') {
                if (debounceTimer) clearTimeout(debounceTimer);
                const delay = config.get('debounceMs', 1500);
                debounceTimer = setTimeout(() => {
                    runAnalysis(event.document);
                }, delay);
            }
        })
    );

    // Run initial analysis on active editor
    if (vscode.window.activeTextEditor &&
        vscode.window.activeTextEditor.document.languageId === 'python') {
        runAnalysis(vscode.window.activeTextEditor.document);
    }

    // Health check on startup
    const config = vscode.workspace.getConfiguration('codesense');
    const backendUrl = config.get('backendUrl', 'http://127.0.0.1:8000');
    checkHealth(backendUrl).then((info) => {
        console.log(`CodeSense backend connected: v${info.version}`);
    }).catch(() => {
        vscode.window.showWarningMessage(
            `CodeSense: Cannot reach backend at ${backendUrl}. ` +
            'Start the server with: uvicorn main:app --host 127.0.0.1 --port 8000'
        );
        updateStatusBar('OFFLINE', 0);
    });
}

/**
 * Run analysis on a document and update diagnostics + status bar.
 * @param {vscode.TextDocument} document
 */
async function runAnalysis(document) {
    const config = vscode.workspace.getConfiguration('codesense');
    const backendUrl = config.get('backendUrl', 'http://127.0.0.1:8000');
    const code = document.getText();

    // Show "analyzing..." in status bar
    statusBarItem.text = '$(sync~spin) Analyzing...';

    try {
        const result = await analyzeCode(backendUrl, code);

        // Cache for hover provider
        lastResult = result;
        lastDocUri = document.uri.toString();

        // Create and set diagnostics
        const diagnostics = createDiagnostics(result, document.uri);
        diagnosticCollection.set(document.uri, diagnostics);

        // Update status bar
        updateStatusBar(result.risk_rating, result.risk_score);

        // Show notification for critical findings
        const criticalCount = result.risk_summary ? result.risk_summary.breakdown.CRITICAL : 0;
        if (criticalCount > 0) {
            vscode.window.showWarningMessage(
                `CodeSense: ${criticalCount} CRITICAL issue(s) detected in ${document.fileName.split(/[\\/]/).pop()}`
            );
        }

    } catch (err) {
        console.error('CodeSense analysis error:', err.message);
        if (diagnosticCollection) {
            diagnosticCollection.delete(document.uri);
        }
        statusBarItem.text = '$(shield) CodeSense (offline)';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
}

/**
 * Update the status bar with the current risk rating.
 * @param {string} rating
 * @param {number} score
 */
function updateStatusBar(rating, score) {
    const icons = {
        'NONE': '$(check)',
        'LOW': '$(info)',
        'MEDIUM': '$(warning)',
        'HIGH': '$(flame)',
        'CRITICAL': '$(error)',
        'OFFLINE': '$(debug-disconnect)'
    };

    const colors = {
        'NONE': undefined,
        'LOW': undefined,
        'MEDIUM': new vscode.ThemeColor('statusBarItem.warningBackground'),
        'HIGH': new vscode.ThemeColor('statusBarItem.errorBackground'),
        'CRITICAL': new vscode.ThemeColor('statusBarItem.errorBackground'),
        'OFFLINE': new vscode.ThemeColor('statusBarItem.warningBackground')
    };

    const icon = icons[rating] || '$(shield)';
    statusBarItem.text = `${icon} CodeSense: ${rating}`;
    statusBarItem.backgroundColor = colors[rating];

    if (rating !== 'OFFLINE') {
        statusBarItem.tooltip = `Risk Score: ${score} | Rating: ${rating}\nClick to re-analyze`;
    }
}

function deactivate() {
    if (debounceTimer) clearTimeout(debounceTimer);
    if (diagnosticCollection) diagnosticCollection.dispose();
    if (statusBarItem) statusBarItem.dispose();
}

module.exports = { activate, deactivate };
