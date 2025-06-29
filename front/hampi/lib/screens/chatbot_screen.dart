import 'package:flutter/material.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';
import 'package:path_provider/path_provider.dart';
import '../models/chat_message.dart';
import '../models/agent.dart';
import '../services/api_service.dart';
import '../widgets/chat_message_widget.dart';

class ChatbotScreen extends StatefulWidget {
  final Agent agent;
  
  const ChatbotScreen({
    super.key,
    required this.agent,
  });

  @override
  State<ChatbotScreen> createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;
  bool _isRecording = false;
  bool _isFirstMessage = true;
  String? _lastDiagnosis;

  @override
  void initState() {
    super.initState();
    _addWelcomeMessage();
  }

  void _addWelcomeMessage() {
    String welcomeMessage = '';
    
    switch (widget.agent.type) {
      case AgentType.dental:
        welcomeMessage = '¡Hola! Soy ${widget.agent.name}, especialista en radiografías dentales. Envíame una imagen de tu radiografía dental para evaluarla. Después podrás hacerme preguntas de seguimiento sobre el diagnóstico.';
        break;
      case AgentType.dermis:
        welcomeMessage = '¡Hola! Soy ${widget.agent.name}, especialista en lesiones dermatológicas. Envíame una foto de tu lesión para evaluarla. Después podrás hacerme preguntas de seguimiento sobre el diagnóstico.';
        break;
      case AgentType.cough:
        welcomeMessage = '¡Hola! Soy ${widget.agent.name}, especialista en análisis de tos. Graba un audio de tu tos para evaluarla. Después podrás hacerme preguntas de seguimiento sobre el diagnóstico.';
        break;
    }

    _messages.add(
      ChatMessage(
        id: const Uuid().v4(),
        content: welcomeMessage,
        type: MessageType.bot,
        timestamp: DateTime.now(),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        await _processImage(File(image.path));
      }
    } catch (e) {
      _showErrorSnackBar('Error al seleccionar la imagen: $e');
    }
  }

  Future<void> _processImage(File imageFile) async {
    if (_isFirstMessage) {
      _isFirstMessage = false;
    }

    final messageId = const Uuid().v4();
    final userMessage = ChatMessage(
      id: messageId,
      content: 'Imagen enviada para evaluación',
      type: MessageType.user,
      timestamp: DateTime.now(),
      status: MessageStatus.sending,
      imagePath: imageFile.path,
      description: _textController.text.isNotEmpty ? _textController.text : null,
      category: MessageCategory.initial,
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      final response = await ApiService.evaluateWithAgent(
        agent: widget.agent,
        imageFile: imageFile,
        description: userMessage.description,
      );

      _handleSuccessfulResponse(userMessage, response, true);
    } catch (e) {
      _handleErrorResponse(userMessage, e.toString());
    }
  }

  Future<void> _startRecording() async {

  }

  Future<void> _stopRecording() async {
    try {
      setState(() {
        _isRecording = false;
      });
    } catch (e) {
      setState(() {
        _isRecording = false;
      });
      _showErrorSnackBar('Error al detener la grabación: $e');
    }
  }

  Future<void> _processAudio(File audioFile) async {
    if (_isFirstMessage) {
      _isFirstMessage = false;
    }

    final messageId = const Uuid().v4();
    final userMessage = ChatMessage(
      id: messageId,
      content: 'Audio enviado para evaluación',
      type: MessageType.user,
      timestamp: DateTime.now(),
      status: MessageStatus.sending,
      audioPath: audioFile.path,
      description: _textController.text.isNotEmpty ? _textController.text : null,
      category: MessageCategory.initial,
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      final response = await ApiService.evaluateWithAgent(
        agent: widget.agent,
        audioFile: audioFile,
        description: userMessage.description,
      );

      _handleSuccessfulResponse(userMessage, response, true);
    } catch (e) {
      _handleErrorResponse(userMessage, e.toString());
    }
  }

  void _handleSuccessfulResponse(ChatMessage userMessage, Map<String, dynamic> response, bool isInitial) {
    final updatedUserMessage = userMessage.copyWith(status: MessageStatus.sent);
    final userIndex = _messages.indexWhere((m) => m.id == userMessage.id);
    if (userIndex != -1) {
      setState(() {
        _messages[userIndex] = updatedUserMessage;
      });
    }

    String diagnosis = '';
    if (isInitial) {
      diagnosis = _formatBotResponse(response);
      _lastDiagnosis = diagnosis;
    }

    final botMessage = ChatMessage(
      id: const Uuid().v4(),
      content: isInitial ? diagnosis : _formatBotResponse(response),
      type: MessageType.bot,
      timestamp: DateTime.now(),
      diagnosis: isInitial ? diagnosis : null,
      category: isInitial ? MessageCategory.initial : MessageCategory.followup,
      showClinicsButton: isInitial,
    );

    setState(() {
      _messages.add(botMessage);
      _isLoading = false;
    });

    _scrollToBottom();
    _textController.clear();
  }

  void _handleErrorResponse(ChatMessage userMessage, String error) {
    final errorUserMessage = userMessage.copyWith(status: MessageStatus.error);
    final userIndex = _messages.indexWhere((m) => m.id == userMessage.id);
    if (userIndex != -1) {
      setState(() {
        _messages[userIndex] = errorUserMessage;
      });
    }

    setState(() {
      _isLoading = false;
    });

    _showErrorSnackBar('Error al procesar: $error');
  }

  String _formatBotResponse(Map<String, dynamic> response) {
    if (response.containsKey('medical_advice')) {
      return response['medical_advice'] ?? 'No se encontró consejo médico';
    }
    
    if (response.containsKey('response')) {
      return response['response'] ?? 'No se encontró respuesta';
    }
    
    return response.toString();
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showInputSourceDialog() {
    if (widget.agent.inputType == 'image') {
      _showImageSourceDialog();
    } else if (widget.agent.inputType == 'audio') {
      _showAudioSourceDialog();
    }
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('Tomar foto'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.photo_library),
                title: const Text('Galería'),
                onTap: () {
                  Navigator.pop(context);
                  _pickImage(ImageSource.gallery);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  void _showAudioSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (BuildContext context) {
        return SafeArea(
          child: Wrap(
            children: [
              ListTile(
                leading: const Icon(Icons.mic),
                title: const Text('Grabar audio'),
                onTap: () {
                  Navigator.pop(context);
                  if (_isRecording) {
                    _stopRecording();
                  } else {
                    _startRecording();
                  }
                },
              ),
            ],
          ),
        );
      },
    );
  }

  Future<void> _sendFollowupQuestion(String userQuestion) async {
    if (_lastDiagnosis == null) {
      _showErrorSnackBar('No hay un diagnóstico previo para hacer preguntas de seguimiento');
      return;
    }

    final messageId = const Uuid().v4();
    final userMessage = ChatMessage(
      id: messageId,
      content: userQuestion,
      type: MessageType.user,
      timestamp: DateTime.now(),
      status: MessageStatus.sending,
      category: MessageCategory.followup,
    );

    setState(() {
      _messages.add(userMessage);
      _isLoading = true;
    });

    _scrollToBottom();

    try {
      final context = _buildContext();
      
      final response = await ApiService.sendFollowupQuestion(
        context: context,
        userPrompt: userQuestion,
      );

      _handleSuccessfulResponse(userMessage, response, false);
    } catch (e) {
      _handleErrorResponse(userMessage, e.toString());
    }
  }

  String _buildContext() {
    final startIndex = _messages.length > 5 ? _messages.length - 5 : 0;
    final recentMessages = _messages.skip(startIndex).take(5).toList();
    final contextMessages = recentMessages.map((msg) => 
      '${msg.type == MessageType.user ? "Usuario" : "Bot"}: ${msg.content}'
    ).join('\n');
    
    return 'Diagnóstico principal: $_lastDiagnosis\n\nConversación reciente:\n$contextMessages';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.agent.name}'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: _messages.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.chat_bubble_outline,
                          size: 64,
                          color: Colors.grey,
                        ),
                        SizedBox(height: 16),
                        Text(
                          'No hay mensajes',
                          style: TextStyle(
                            fontSize: 18,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.only(top: 8, bottom: 8),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      return ChatMessageWidget(
                        message: _messages[index],
                        isLastMessage: index == _messages.length - 1,
                      );
                    },
                  ),
          ),
          if (_isLoading)
            Container(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  const SizedBox(width: 16),
                  Text('Procesando ${widget.agent.inputType == 'image' ? 'imagen' : 'audio'}...'),
                ],
              ),
            ),
          if (_isRecording)
            Container(
              padding: const EdgeInsets.all(16),
              color: Colors.red.withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.mic, color: Colors.red),
                  const SizedBox(width: 16),
                  const Text('Grabando audio...'),
                  const Spacer(),
                  TextButton(
                    onPressed: _stopRecording,
                    child: const Text('Detener'),
                  ),
                ],
              ),
            ),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                IconButton(
                  onPressed: _isLoading || _isRecording ? null : _showInputSourceDialog,
                  icon: Icon(
                    widget.agent.inputType == 'image' ? Icons.camera_alt : Icons.mic,
                  ),
                  tooltip: widget.agent.inputType == 'image' ? 'Enviar imagen' : 'Grabar audio',
                ),
                Expanded(
                  child: TextField(
                    controller: _textController,
                    enabled: !_isLoading && !_isRecording,
                    decoration: InputDecoration(
                      hintText: _lastDiagnosis != null 
                          ? 'Haz una pregunta de seguimiento...'
                          : widget.agent.inputType == 'image' 
                              ? 'Descripción de la lesión (opcional)...'
                              : 'Descripción del audio (opcional)...',
                      border: const OutlineInputBorder(
                        borderRadius: BorderRadius.all(Radius.circular(24)),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    maxLines: null,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: (_isLoading || _isRecording) ? null : () {
                    if (_textController.text.isNotEmpty) {
                      if (_lastDiagnosis != null) {
                        _sendFollowupQuestion(_textController.text);
                      } else {
                        _showErrorSnackBar('Primero debes enviar una imagen o audio para evaluación');
                        _textController.clear();
                      }
                    }
                  },
                  icon: const Icon(Icons.send),
                  tooltip: 'Enviar',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 