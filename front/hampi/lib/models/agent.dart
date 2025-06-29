import 'package:flutter/material.dart';

enum AgentType {
  dental,
  dermis,
  cough,
}

class Agent {
  final String id;
  final String name;
  final String description;
  final String endpoint;
  final AgentType type;
  final IconData icon;
  final String inputType;

  const Agent({
    required this.id,
    required this.name,
    required this.description,
    required this.endpoint,
    required this.type,
    required this.icon,
    required this.inputType,
  });
}

class AgentData {
  static const List<Agent> agents = [
    Agent(
      id: 'dental',
      name: 'Dr. Sonrisa',
      description: 'Especialista en radiografías dentales',
      endpoint: '/dental/evaluate',
      type: AgentType.dental,
      icon: Icons.medical_services,
      inputType: 'image',
    ),
    Agent(
      id: 'dermis',
      name: 'Dr. Piel',
      description: 'Especialista en lesiones dermatológicas',
      endpoint: '/dermis/evaluate',
      type: AgentType.dermis,
      icon: Icons.face,
      inputType: 'image',
    ),
    Agent(
      id: 'cough',
      name: 'Dr. Tos',
      description: 'Especialista en análisis de tos',
      endpoint: '/cough/evaluate',
      type: AgentType.cough,
      icon: Icons.mic,
      inputType: 'audio',
    ),
  ];

  static Agent getAgentById(String id) {
    return agents.firstWhere((agent) => agent.id == id);
  }
} 