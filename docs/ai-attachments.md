# AI Attachments Feature

The LLM Council now supports multimodal interactions, allowing users to send images and files (PDFs, text files) along with their text queries.

## How to Use

1.  **Attach Files**: Click the paperclip icon in the chat input area.
2.  **Select Files**: Choose one or more images (PNG, JPEG, WEBP, GIF) or files (PDF, TXT).
    *   **Max Size**: 5MB per file.
3.  **Preview**: Selected files will appear above the input box. You can remove them by clicking the "×" button.
4.  **Send**: Type your question and click "Send". The council models will receive both your text and the attached files.

## Technical Implementation

### Frontend
*   **File Selection**: The `ChatInterface` component handles file selection and converts files to Base64 strings.
*   **Validation**: Files are checked for size (max 5MB) and type before being accepted.
*   **API**: The `api.js` client sends the `attachments` array as part of the `sendMessageStream` payload.

### Backend
*   **API Endpoint**: The `SendMessageRequest` model in `main.py` accepts an optional `attachments` list.
*   **OpenRouter Integration**:
    *   **Images**: Converted to OpenRouter's `image_url` format.
    *   **Files**: Converted to OpenRouter's `file` format (which supports PDF parsing).
*   **Council Process**: Attachments are passed through all 3 stages of the council:
    1.  **Stage 1 (Individual Opinions)**: Models see the attachments to answer the initial query.
    2.  **Stage 2 (Peer Review)**: Models see the attachments again to properly evaluate if the peer responses are accurate regarding the file content.
    3.  **Stage 3 (Chairman Synthesis)**: The Chairman sees the attachments to synthesize the final answer.

## Supported Formats

*   **Images**: `image/png`, `image/jpeg`, `image/webp`, `image/gif`
*   **Documents**: `application/pdf`, `text/plain`

## Limitations

*   **File Size**: Strictly limited to 5MB per file to prevent timeouts and excessive token usage.
*   **Cost**: Multimodal requests (especially with high-res images or long PDFs) consume significantly more tokens than text-only requests.
