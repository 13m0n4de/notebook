# Rust

```rust title="main.rs" linenums="1" hl_lines="2-6"
#[derive(Serialize)]
struct AnswerResponse {
    status: bool,
    score: u8,
    message: String,
}

static INFO: OnceLock<Info> = OnceLock::new();
static ANSWERS: OnceLock<HashMap<usize, (Vec<String>, u8)>> = OnceLock::new();
static FLAG: OnceLock<String> = OnceLock::new();
static MESSAGE: OnceLock<Message> = OnceLock::new();

async fn get_info() -> Json<Info> {
    let info = INFO.get().unwrap();
    Json(info.clone())
}
```
