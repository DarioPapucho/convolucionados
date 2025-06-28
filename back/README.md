# Convolucionados API

API for AI services using Google Gemini and image classification with Hugging Face, with clean architecture.

## Project Structure

```
src/
├── api/
│   └── routes/
│       ├── chat_routes.py         # Chat routes with Gemini
│       └── lesion_routes.py       # Lesion evaluation routes
├── domain/
│   ├── dtos/
│   │   ├── chat_request.py        # DTO for chat requests
│   │   ├── chat_response.py       # DTO for chat responses
│   │   ├── lesion_evaluation_request.py   # DTO for lesion evaluation
│   │   ├── lesion_evaluation_response.py  # DTO for lesion responses
│   │   └── image_request.py       # DTO for image requests
│   └── interfaces/
│       ├── dialog_system_service.py       # Dialog service interface
│       └── vision_classifier_service_interface.py  # Classification interface
├── infrastructure/
│   └── services/
│       ├── gemini_service.py      # Gemini implementation
│       └── huggingface_vision_service.py  # Hugging Face implementation
└── main.py                        # Main application
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.example .env
# Edit .env and add your GEMINI_API_KEY
```

## Usage

### Start the server

```bash
uvicorn src.main:app --reload
```

### Available endpoints

#### POST /chat/generate
Generate a response using Gemini.

**Body:**
```json
{
  "system_prompt": "You are a helpful assistant that responds clearly and concisely.",
  "user_prompt": "What is the capital of France?",
  "context": "The user is studying European geography."
}
```

#### POST /lesion/evaluate
Evaluate a dermatological lesion using image classification and medical advice.

**Form Data:**
- `image`: Image file (required)
- `description`: Optional description of the lesion

**Response:**
```json
{
  "classification": "Melanoma (Confidence: 85%)",
  "medical_advice": "Based on the classification, immediate consultation with a dermatologist is recommended..."
}
```

#### GET /
Root endpoint that shows API information.

## Architecture

The project follows clean architecture principles:

- **Domain**: Contains interfaces and DTOs
- **Infrastructure**: Concrete implementations of services
- **API**: Presentation layer with FastAPI

### Interfaces

- `DialogSystemServiceInterface`: Defines contract for dialog services
- `VisionClassifierServiceInterface`: Defines contract for image classification
- `ChatRequestDTO`: Data structure for chat requests
- `ChatResponseDTO`: Data structure for chat responses
- `LesionEvaluationRequestDTO`: Structure for lesion evaluation
- `LesionEvaluationResponseDTO`: Structure for lesion responses

### Services

- `GeminiService`: Dialog service implementation using Google Gemini
- `HuggingFaceVisionService`: Image classification implementation using Hugging Face

### Lesion Evaluation Flow

1. **Classification**: Hugging Face service classifies the image
2. **Medical Analysis**: Gemini analyzes the classification and generates medical advice
3. **Response**: Both classification and medical advice are returned

## Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (required)

## Main Dependencies

- `fastapi`: Web framework
- `google-generativeai`: Google Gemini API
- `torch`: PyTorch for ML models
- `transformers`: Hugging Face Transformers
- `pillow`: Image processing

## API Documentation

Once the server is running, you can access the automatic documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### - ![Image](flowdiagram.png)