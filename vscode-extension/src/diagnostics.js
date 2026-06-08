const vscode = require('vscode');

/**
 * Severity mapping from CodeSense backend to VS Code DiagnosticSeverity.
 */
const SEVERITY_MAP = {
    'CRITICAL': vscode.DiagnosticSeverity.Error,
    'HIGH': vscode.DiagnosticSeverity.Error,
    'MEDIUM': vscode.DiagnosticSeverity.Warning,
    'LOW': vscode.DiagnosticSeverity.Information
};

/**
 * Convert backend analysis results into VS Code Diagnostics.
 *
 * @param {object} result - The full analysis result from the backend
 * @param {vscode.Uri} uri - The URI of the document being analyzed
 * @returns {vscode.Diagnostic[]} Array of VS Code diagnostics
 */
function createDiagnostics(result, uri) {
    const diagnostics = [];

    // --- Security Risk Diagnostics ---
    if (result.risks && Array.isArray(result.risks)) {
        for (const risk of result.risks) {
            const startLine = Math.max(0, (risk.start_line || 1) - 1);
            const startCol = risk.start_column || 0;
            const endLine = Math.max(0, (risk.end_line || risk.start_line || 1) - 1);
            const endCol = risk.end_column || 200;

            const range = new vscode.Range(startLine, startCol, endLine, endCol);
            const severity = SEVERITY_MAP[risk.severity] || vscode.DiagnosticSeverity.Warning;

            const diagnostic = new vscode.Diagnostic(
                range,
                `[${risk.type}] ${risk.description}`,
                severity
            );
            diagnostic.source = 'CodeSense AI';
            diagnostic.code = risk.type;
            diagnostics.push(diagnostic);
        }
    }

    // --- Architecture Smell Diagnostics ---
    if (result.architecture_smells && Array.isArray(result.architecture_smells)) {
        for (const smell of result.architecture_smells) {
            // Try to find the function's line from the functions list
            let line = 0;
            if (result.functions && Array.isArray(result.functions)) {
                const targetFuncName = smell.function.includes(' → ')
                    ? smell.function.split(' → ')[0].trim()
                    : smell.function;
                const fn = result.functions.find(f => f.name === targetFuncName);
                if (fn) {
                    line = Math.max(0, (fn.start_line || 1) - 1);
                }
            }

            const range = new vscode.Range(line, 0, line, 200);
            const smellSeverity = smell.severity === 'HIGH'
                ? vscode.DiagnosticSeverity.Warning
                : vscode.DiagnosticSeverity.Information;

            const diagnostic = new vscode.Diagnostic(
                range,
                `[${smell.smell}] ${smell.detail || smell.function}`,
                smellSeverity
            );
            diagnostic.source = 'CodeSense AI';
            diagnostic.code = smell.smell;
            diagnostics.push(diagnostic);
        }
    }

    return diagnostics;
}

/**
 * Build a hover markdown string from analysis results for a given position.
 *
 * @param {object} result - The full analysis result
 * @param {vscode.Position} position - The hover position
 * @returns {vscode.MarkdownString|null}
 */
function getHoverInfo(result, position) {
    const line = position.line + 1; // Convert to 1-indexed
    const parts = [];

    // Check risks at this line
    if (result.risks) {
        for (const risk of result.risks) {
            if (risk.start_line <= line && line <= risk.end_line) {
                const icon = risk.severity === 'CRITICAL' ? '🔴' :
                             risk.severity === 'HIGH' ? '🟠' :
                             risk.severity === 'MEDIUM' ? '🟡' : '🔵';
                parts.push(`${icon} **${risk.type}** (${risk.severity})\n\n${risk.description}`);
            }
        }
    }

    // Check function info at this line
    if (result.functions) {
        for (const fn of result.functions) {
            if (fn.start_line <= line && line <= fn.end_line) {
                const complexity = result.complexity ? result.complexity[fn.name] : '?';
                const nesting = result.nesting_depth ? result.nesting_depth[fn.name] : '?';
                const loc = result.lines_of_code ? result.lines_of_code[fn.name] : '?';
                parts.push(
                    `📊 **Function: ${fn.name}**\n\n` +
                    `| Metric | Value |\n|---|---|\n` +
                    `| Cyclomatic Complexity | ${complexity} |\n` +
                    `| Max Nesting Depth | ${nesting} |\n` +
                    `| Lines of Code | ${loc} |\n` +
                    `| Parameters | ${fn.parameters ? fn.parameters.join(', ') : 'none'} |`
                );
            }
        }
    }

    if (parts.length === 0) return null;

    const md = new vscode.MarkdownString(parts.join('\n\n---\n\n'));
    md.isTrusted = true;
    return md;
}

module.exports = { createDiagnostics, getHoverInfo };
