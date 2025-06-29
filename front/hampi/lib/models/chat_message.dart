enum MessageType {
  user,
  bot,
}

enum MessageStatus {
  sending,
  sent,
  error,
}

enum MessageCategory {
  initial,
  followup,
}

class ChatMessage {
  final String id;
  final String content;
  final MessageType type;
  final DateTime timestamp;
  final MessageStatus status;
  final String? imagePath;
  final String? audioPath;
  final String? description;
  final String? diagnosis;
  final MessageCategory category;
  final bool showClinicsButton;

  ChatMessage({
    required this.id,
    required this.content,
    required this.type,
    required this.timestamp,
    this.status = MessageStatus.sent,
    this.imagePath,
    this.audioPath,
    this.description,
    this.diagnosis,
    this.category = MessageCategory.initial,
    this.showClinicsButton = false,
  });

  ChatMessage copyWith({
    String? id,
    String? content,
    MessageType? type,
    DateTime? timestamp,
    MessageStatus? status,
    String? imagePath,
    String? audioPath,
    String? description,
    String? diagnosis,
    MessageCategory? category,
    bool? showClinicsButton,
  }) {
    return ChatMessage(
      id: id ?? this.id,
      content: content ?? this.content,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      status: status ?? this.status,
      imagePath: imagePath ?? this.imagePath,
      audioPath: audioPath ?? this.audioPath,
      description: description ?? this.description,
      diagnosis: diagnosis ?? this.diagnosis,
      category: category ?? this.category,
      showClinicsButton: showClinicsButton ?? this.showClinicsButton,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'type': type.name,
      'timestamp': timestamp.toIso8601String(),
      'status': status.name,
      'imagePath': imagePath,
      'audioPath': audioPath,
      'description': description,
      'diagnosis': diagnosis,
      'category': category.name,
      'showClinicsButton': showClinicsButton,
    };
  }

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'],
      content: json['content'],
      type: MessageType.values.firstWhere((e) => e.name == json['type']),
      timestamp: DateTime.parse(json['timestamp']),
      status: MessageStatus.values.firstWhere((e) => e.name == json['status']),
      imagePath: json['imagePath'],
      audioPath: json['audioPath'],
      description: json['description'],
      diagnosis: json['diagnosis'],
      category: MessageCategory.values.firstWhere((e) => e.name == json['category']),
      showClinicsButton: json['showClinicsButton'] ?? false,
    );
  }
} 