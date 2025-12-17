# Python to Spring Boot Migration Plan

## Executive Summary

This document outlines a comprehensive plan to migrate the LLM Council backend from **Python/FastAPI** to **Spring Boot/Java with Gradle**. The migration will create a parallel Java backend that maintains API compatibility with the existing frontend while leveraging Spring Boot's enterprise-grade features.

**Key Metrics:**
- **Files to migrate:** 4 core Python modules
- **Total lines of Python code:** ~650 LOC
- **Estimated Java code:** ~1,200 LOC (higher due to type safety and boilerplate)
- **API endpoints:** 5 REST endpoints (1 SSE streaming)
- **External dependencies:** OpenRouter API integration

## Current Architecture Analysis

### Python Backend Structure

```
backend/
├── __init__.py          # Package initialization
├── config.py            # Configuration (models, API keys)
├── main.py              # FastAPI application (routes, CORS, SSE)
├── council.py           # 3-stage council orchestration
├── openrouter.py        # OpenRouter API client
└── storage.py           # JSON file-based storage
```

### Key Components Breakdown

#### 1. main.py - FastAPI Application (216 lines)
**Responsibilities:**
- REST API endpoint definitions
- CORS middleware configuration
- Request/Response models (Pydantic)
- Server-Sent Events (SSE) streaming for real-time updates
- Error handling (HTTPException)

**Key Features:**
- `GET /` - Health check
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation details
- `POST /api/conversations/{id}/message` - Send message (synchronous)
- `POST /api/conversations/{id}/message/stream` - Send message (SSE streaming)

**Technologies:**
- FastAPI framework
- Pydantic for validation
- Async/await for concurrency
- StreamingResponse for SSE

#### 2. council.py - Council Orchestration (402 lines)
**Responsibilities:**
- 3-stage council process implementation
- Message formatting with multimodal attachments
- Parallel LLM querying
- Response aggregation and ranking
- Title generation

**Key Functions:**
- `stage1_collect_responses()` - Query all models in parallel
- `stage2_collect_rankings()` - Models rank each other's responses
- `stage3_synthesize_final()` - Chairman synthesizes final answer
- `calculate_aggregate_rankings()` - Aggregate ranking scores
- `parse_ranking_from_text()` - Extract rankings using regex
- `generate_conversation_title()` - Auto-generate conversation title
- `format_user_message()` - Handle text + image/file attachments

**Technologies:**
- Asyncio for parallel execution
- Base64 encoding/decoding for attachments
- Regular expressions for parsing

#### 3. openrouter.py - API Client
**Responsibilities:**
- HTTP client for OpenRouter API
- Parallel model querying
- Request/response formatting
- Error handling and timeouts

**Key Features:**
- Async HTTP requests using httpx
- Parallel execution with asyncio.gather()
- Configurable timeouts (180s default)
- Multimodal content support

#### 4. storage.py - File Storage (179 lines)
**Responsibilities:**
- JSON-based conversation persistence
- CRUD operations for conversations
- Message management
- File system operations

**Data Model:**
```json
{
  "id": "uuid",
  "created_at": "ISO timestamp",
  "title": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "attachments": []
    }
  ]
}
```

#### 5. config.py - Configuration
**Responsibilities:**
- Environment variable loading
- Model configuration
- API endpoints and keys
- File upload limits

---

## Proposed Java Architecture

### Directory Structure

```
backend-java/
├── gradle/
│   └── wrapper/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/yourname/llmcouncil/
│   │   │       ├── LlmCouncilApplication.java       # Spring Boot main class
│   │   │       ├── config/
│   │   │       │   ├── CorsConfig.java              # CORS configuration
│   │   │       │   ├── WebClientConfig.java         # HTTP client config
│   │   │       │   └── LlmCouncilProperties.java    # Application properties
│   │   │       ├── controller/
│   │   │       │   └── ConversationController.java  # REST endpoints
│   │   │       ├── service/
│   │   │       │   ├── CouncilService.java          # 3-stage orchestration
│   │   │       │   ├── StorageService.java          # File persistence
│   │   │       │   └── TitleGenerationService.java  # Title generation
│   │   │       ├── client/
│   │   │       │   └── OpenRouterClient.java        # OpenRouter integration
│   │   │       ├── model/
│   │   │       │   ├── dto/                         # Request/Response DTOs
│   │   │       │   │   ├── CreateConversationRequest.java
│   │   │       │   │   ├── SendMessageRequest.java
│   │   │       │   │   ├── Attachment.java
│   │   │       │   │   ├── ConversationDto.java
│   │   │       │   │   └── ConversationMetadataDto.java
│   │   │       │   └── entity/                      # Data models
│   │   │       │       ├── Conversation.java
│   │   │       │       ├── Message.java
│   │   │       │       └── StageResult.java
│   │   │       └── util/
│   │   │           ├── MessageFormatter.java        # Multimodal formatting
│   │   │           └── RankingParser.java           # Ranking text parser
│   │   └── resources/
│   │       ├── application.yml                      # Spring configuration
│   │       └── application-dev.yml                  # Dev-specific config
│   └── test/
│       └── java/
│           └── com/yourname/llmcouncil/
│               ├── service/
│               └── client/
├── build.gradle
├── settings.gradle
├── gradlew
├── gradlew.bat
└── README.md
```

---

## Component Migration Mapping

### 1. main.py → ConversationController.java

**Python (FastAPI):**
```python
@app.post("/api/conversations/{conversation_id}/message/stream")
async def send_message_stream(conversation_id: str, request: SendMessageRequest):
    async def event_generator():
        yield f"data: {json.dumps({'type': 'stage1_start'})}\\n\\n"
        # ... streaming logic
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Java (Spring Boot):**
```java
@RestController
@RequestMapping("/api/conversations")
public class ConversationController {
    
    @PostMapping("/{conversationId}/message/stream")
    public Flux<ServerSentEvent<Map<String, Object>>> sendMessageStream(
            @PathVariable String conversationId,
            @RequestBody SendMessageRequest request) {
        
        return councilService.processMessageStream(conversationId, request)
            .map(event -> ServerSentEvent.<Map<String, Object>>builder()
                .data(event)
                .build());
    }
}
```

**Key Changes:**
- `@RestController` instead of `@app` decorators
- `Flux<ServerSentEvent>` for SSE streaming (WebFlux)
- Dependency injection via constructor
- Strong typing with generics

---

### 2. council.py → CouncilService.java

**Python (AsyncIO):**
```python
async def stage1_collect_responses(user_query: str, attachments: List[Dict] = None):
    messages = [format_user_message(user_query, attachments)]
    responses = await query_models_parallel(COUNCIL_MODELS, messages)
    return stage1_results
```

**Java (CompletableFuture):**
```java
@Service
public class CouncilService {
    
    public CompletableFuture<List<Stage1Result>> stage1CollectResponses(
            String userQuery, List<Attachment> attachments) {
        
        Message message = messageFormatter.format(userQuery, attachments);
        
        List<CompletableFuture<Stage1Result>> futures = councilModels.stream()
            .map(model -> openRouterClient.queryModel(model, List.of(message)))
            .collect(Collectors.toList());
        
        return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .thenApply(v -> futures.stream()
                .map(CompletableFuture::join)
                .collect(Collectors.toList()));
    }
}
```

**Key Changes:**
- `CompletableFuture` instead of `async/await`
- Java Streams API for parallel processing
- `@Service` annotation for dependency injection
- Explicit error handling with try-catch or `.exceptionally()`

---

### 3. openrouter.py → OpenRouterClient.java

**Python (httpx):**
```python
async def query_model(model: str, messages: list, timeout: float = 180.0):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_API_URL,
            json={"model": model, "messages": messages},
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        return response.json()
```

**Java (WebClient):**
```java
@Component
public class OpenRouterClient {
    
    private final WebClient webClient;
    
    public CompletableFuture<OpenRouterResponse> queryModel(
            String model, List<Message> messages) {
        
        return webClient.post()
            .uri("/chat/completions")
            .header("Authorization", "Bearer " + apiKey)
            .bodyValue(new OpenRouterRequest(model, messages))
            .retrieve()
            .bodyToMono(OpenRouterResponse.class)
            .timeout(Duration.ofSeconds(180))
            .toFuture();
    }
}
```

**Key Changes:**
- `WebClient` (reactive) instead of httpx
- Mono/Flux for reactive streams
- Builder pattern for requests
- Type-safe request/response models

---

### 4. storage.py → StorageService.java

**Python (JSON files):**
```python
def save_conversation(conversation: Dict[str, Any]):
    path = get_conversation_path(conversation['id'])
    with open(path, 'w') as f:
        json.dump(conversation, f, indent=2)
```

**Java (Jackson + NIO):**
```java
@Service
public class StorageService {
    
    private final ObjectMapper objectMapper;
    private final Path dataDir;
    
    public void saveConversation(Conversation conversation) throws IOException {
        Path filePath = dataDir.resolve(conversation.getId() + ".json");
        objectMapper.writerWithDefaultPrettyPrinter()
            .writeValue(filePath.toFile(), conversation);
    }
    
    public Conversation getConversation(String id) throws IOException {
        Path filePath = dataDir.resolve(id + ".json");
        if (!Files.exists(filePath)) {
            return null;
        }
        return objectMapper.readValue(filePath.toFile(), Conversation.class);
    }
}
```

**Key Changes:**
- Jackson `ObjectMapper` for JSON serialization
- Java NIO `Path` API for file operations
- Type-safe entity classes
- Explicit exception handling

---

### 5. config.py → Application Configuration

**Python (.env + config.py):**
```python
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
COUNCIL_MODELS = ["openai/gpt-5.1", "google/gemini-3-pro-preview", ...]
DATA_DIR = "data/conversations"
```

**Java (application.yml + @ConfigurationProperties):**

**application.yml:**
```yaml
llm-council:
  openrouter:
    api-key: ${OPENROUTER_API_KEY}
    api-url: https://openrouter.ai/api/v1/chat/completions
  council:
    models:
      - openai/gpt-5.1
      - google/gemini-3-pro-preview
      - anthropic/claude-sonnet-4.5
      - x-ai/grok-4.1-fast
    chairman-model: openai/gpt-5.1
  storage:
    data-dir: data/conversations
  upload:
    max-file-size: 5242880  # 5MB
```

**LlmCouncilProperties.java:**
```java
@Configuration
@ConfigurationProperties(prefix = "llm-council")
@Validated
public class LlmCouncilProperties {
    
    @NotNull
    private OpenRouterConfig openrouter;
    
    @NotNull
    private CouncilConfig council;
    
    @NotNull
    private StorageConfig storage;
    
    // Getters, setters, nested classes
    
    public static class OpenRouterConfig {
        @NotBlank
        private String apiKey;
        private String apiUrl;
        // getters/setters
    }
    
    // ... other nested config classes
}
```

---

## Technology Stack Comparison

| Component | Python Stack | Java Stack | Notes |
|-----------|-------------|------------|-------|
| **Web Framework** | FastAPI | Spring Boot 3.x + Spring WebFlux | WebFlux for reactive SSE |
| **Build Tool** | uv/pip | Gradle 8.x | Gradle wrapper for consistency |
| **HTTP Client** | httpx (async) | WebClient (reactive) | Both support async operations |
| **JSON** | Built-in json | Jackson | Jackson is Spring Boot default |
| **Validation** | Pydantic | Bean Validation (JSR-303) | Hibernate Validator impl |
| **Async** | asyncio | CompletableFuture / Reactor | Reactor for reactive streams |
| **Config** | python-dotenv | Spring Boot @ConfigurationProperties | Type-safe config binding |
| **Testing** | pytest | JUnit 5 + Mockito | Spring Test support |

---

## Detailed Gradle Configuration

### build.gradle

```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.yourname'
version = '1.0.0'
sourceCompatibility = '17'

configurations {
    compileOnly {
        extendsFrom annotationProcessor
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot Starters
    implementation 'org.springframework.boot:spring-boot-starter-webflux'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    
    // Jackson for JSON
    implementation 'com.fasterxml.jackson.core:jackson-databind'
    implementation 'com.fasterxml.jackson.datatype:jackson-datatype-jsr310'
    
    // Lombok (reduce boilerplate)
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    
    // Testing
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'io.projectreactor:reactor-test'
    
    // Dev tools
    developmentOnly 'org.springframework.boot:spring-boot-devtools'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

---

## Migration Strategy

### Phase 1: Setup (1-2 days)

**Tasks:**
1. ✅ Initialize Spring Boot project with Gradle
2. ✅ Set up project structure
3. ✅ Configure build.gradle with dependencies
4. ✅ Create application.yml with configuration
5. ✅ Set up CORS configuration
6. ✅ Create base entity and DTO classes

**Deliverables:**
- Runnable Spring Boot application
- Basic health check endpoint working
- Configuration loaded from environment

---

### Phase 2: Core Services (3-4 days)

**Priority Order:**

#### Step 1: Storage Service
- Lowest complexity, no external dependencies
- Implement JSON file read/write with Jackson
- Test conversation CRUD operations

#### Step 2: OpenRouter Client
- Implement WebClient-based HTTP client
- Handle authentication headers
- Test with actual OpenRouter API

#### Step 3: Message Formatting Utilities
- Convert `format_user_message()` function
- Handle multimodal content (text, images, files)
- Base64 encoding/decoding

#### Step 4: Council Service
- Implement 3-stage process logic
- Parallel execution with CompletableFuture
- Response aggregation and ranking

---

### Phase 3: REST API (2-3 days)

**Tasks:**
1. Implement synchronous endpoints:
   - `GET /` health check
   - `GET /api/conversations` list
   - `POST /api/conversations` create
   - `GET /api/conversations/{id}` get
   - `POST /api/conversations/{id}/message` send
   
2. Implement SSE streaming endpoint:
   - `POST /api/conversations/{id}/message/stream`
   - Use `Flux<ServerSentEvent>`
   - Progressive event emission

3. Error handling:
   - Global exception handler
   - Custom exceptions
   - Proper HTTP status codes

---

### Phase 4: Testing & Validation (2-3 days)

**Strategy:**

1. **Unit Tests:**
   - Service layer tests with mocked dependencies
   - RankingParser regex logic tests
   - MessageFormatter tests

2. **Integration Tests:**
   - Full end-to-end API tests
   - Test with actual file storage
   - Mock OpenRouter responses

3. **Comparison Testing:**
   - Run both Python and Java backends
   - Send identical requests
   - Compare responses for consistency

---

### Phase 5: Deployment & Cutover (1-2 days)

**Steps:**

1. **Parallel Deployment:**
   - Run Java backend on port 8080
   - Keep Python backend on port 8001
   - Create startup scripts for both

2. **Frontend Switch:**
   - Update `frontend/src/api.js`:
     ```javascript
     const API_BASE = 'http://localhost:8080';
     ```
   - Test all frontend features

3. **Monitoring Period:**
   - Monitor for errors/issues
   - Compare performance metrics
   - Keep Python backend as fallback

4. **Documentation:**
   - Update README.md
   - Document Java-specific setup
   - Migration notes

---

## Key Implementation Challenges

### 1. Server-Sent Events (SSE) Streaming

**Challenge:** Python's `async def event_generator()` → Java reactive streams

**Solution:**
```java
public Flux<ServerSentEvent<Map<String, Object>>> processMessageStream(
        String conversationId, SendMessageRequest request) {
    
    return Flux.create(sink -> {
        // Emit stage1_start
        sink.next(createEvent("stage1_start", null));
        
        stage1CollectResponses(request.getContent(), request.getAttachments())
            .thenAccept(stage1Results -> {
                sink.next(createEvent("stage1_complete", stage1Results));
                
                // Continue with stage2, stage3...
            })
            .exceptionally(error -> {
                sink.error(error);
                return null;
            });
    });
}
```

**Alternative:** Use `SseEmitter` with Spring MVC (simpler, non-reactive)

---

### 2. Parallel Async Execution

**Challenge:** Python's `asyncio.gather()` → Java parallel execution

**Solution:**
```java
List<CompletableFuture<Response>> futures = models.stream()
    .map(model -> openRouterClient.queryModel(model, messages))
    .collect(Collectors.toList());

CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
    .thenApply(v -> futures.stream()
        .map(CompletableFuture::join)
        .filter(Objects::nonNull)  // Filter failed responses
        .collect(Collectors.toList()));
```

---

### 3. Regex Parsing for Rankings

**Challenge:** Port Python regex logic to Java

**Solution:** Nearly identical, Java has excellent regex support
```java
public List<String> parseRanking(String rankingText) {
    if (rankingText.contains("FINAL RANKING:")) {
        String rankingSection = rankingText.split("FINAL RANKING:")[1];
        Pattern pattern = Pattern.compile("\\d+\\.\\s*Response [A-Z]");
        Matcher matcher = pattern.matcher(rankingSection);
        
        List<String> results = new ArrayList<>();
        while (matcher.find()) {
            results.add(matcher.group());
        }
        return results;
    }
    return Collections.emptyList();
}
```

---

## Testing Strategy

### Unit Tests

```java
@SpringBootTest
class CouncilServiceTest {
    
    @MockBean
    private OpenRouterClient openRouterClient;
    
    @Autowired
    private CouncilService councilService;
    
    @Test
    void testStage1CollectResponses() {
        // Mock responses
        when(openRouterClient.queryModel(any(), any()))
            .thenReturn(CompletableFuture.completedFuture(mockResponse));
        
        // Test
        List<Stage1Result> results = councilService
            .stage1CollectResponses("test query", null)
            .join();
        
        // Verify
        assertThat(results).hasSize(4);
        verify(openRouterClient, times(4)).queryModel(any(), any());
    }
}
```

---

## Performance Considerations

### Python (Current)
- **Async I/O:** asyncio event loop
- **Concurrency:** True async with httpx
- **Memory:** Efficient for I/O-bound tasks
- **Startup Time:** ~1-2 seconds

### Java (Expected)
- **Async I/O:** Project Reactor (WebFlux)
- **Concurrency:** CompletableFuture thread pools
- **Memory:** Higher baseline (~100MB vs ~30MB)
- **Startup Time:** ~3-5 seconds (Spring Boot)

**Trade-offs:**
- Java: Better type safety, tooling, debugging
- Python: Faster startup, lower memory footprint
- Both: Similar runtime performance for I/O-bound work

---

## Estimated Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Setup | 1-2 days | 8-16 hours |
| Phase 2: Core Services | 3-4 days | 24-32 hours |
| Phase 3: REST API | 2-3 days | 16-24 hours |
| Phase 4: Testing | 2-3 days | 16-24 hours |
| Phase 5: Deployment | 1-2 days | 8-16 hours |
| **Total** | **9-14 days** | **72-112 hours** |

**Note:** Timeline assumes:
- 1 developer working full-time
- Familiarity with both Python and Java
- No major API changes required
- Incremental testing throughout

---

## Rollback Plan

If issues arise during migration:

1. **Keep Python Backend Running**
   - Maintain `backend/` directory
   - Document as `backend-python/` for clarity

2. **Quick Switch:**
   ```javascript
   // frontend/src/api.js
   const API_BASE = 'http://localhost:8001';  // Back to Python
   ```

3. **Parallel Running:**
   - Python on :8001
   - Java on :8080
   - Feature flags for gradual migration

---

## Recommended Next Steps

1. **Decision Checkpoint:**
   - Review this migration plan
   - Confirm business/technical justification
   - Approve timeline and resource allocation

2. **If Proceeding:**
   - Create `backend-java/` directory
   - Initialize Spring Boot project with Spring Initializr
   - Set up Gradle wrapper
   - Begin Phase 1 (Setup)

3. **If Delaying:**
   - Document this plan for future reference
   - Continue with Python backend
   - Revisit decision in 3-6 months

---

## Conclusion

This migration is **technically feasible** and well-scoped. The Python codebase is clean and well-structured, making it straightforward to port to Java/Spring Boot.

**Recommendation:** Only proceed if you have a clear business driver (team expertise, enterprise requirements, etc.). The current Python implementation is production-ready and performant.

**If proceeding:** Follow the phased approach outlined above, maintaining the Python backend in parallel until the Java version is fully validated.
