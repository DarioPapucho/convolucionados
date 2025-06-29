import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/agent.dart';
import '../models/clinic.dart';

class ApiService {
  static String get baseUrl => AppConfig.serverUrl;

  static Future<Map<String, dynamic>> evaluateWithAgent({
    required Agent agent,
    File? imageFile,
    File? audioFile,
    String? description,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl${agent.endpoint}'),
      );

      request.headers['accept'] = 'application/json; charset=utf-8';
      request.headers['content-type'] = 'multipart/form-data; charset=utf-8';

      if (agent.inputType == 'image' && imageFile != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'image',
            imageFile.path,
            filename: imageFile.path.split('/').last,
          ),
        );
      } else if (agent.inputType == 'audio' && audioFile != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'audio',
            audioFile.path,
            filename: audioFile.path.split('/').last,
          ),
        );
      }

      if (description != null && description.isNotEmpty) {
        request.fields['description'] = description;
      }

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode == 200) {
        final decodedResponse = json.decode(utf8.decode(response.bodyBytes));
        return decodedResponse;
      } else {
        throw Exception('Error en la petición: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  static Future<Map<String, dynamic>> sendFollowupQuestion({
    required String context,
    required String userPrompt,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat/generate'),
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'accept': 'application/json; charset=utf-8',
        },
        body: json.encode({
          'context': context,
          'system_prompt': '',
          'user_prompt': userPrompt,
        }),
      );

      if (response.statusCode == 200) {
        final decodedResponse = json.decode(utf8.decode(response.bodyBytes));
        return decodedResponse;
      } else {
        throw Exception('Error en la petición: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  static Future<Map<String, dynamic>> evaluateLesion({
    required File imageFile,
    required String description,
  }) async {
    return evaluateWithAgent(
      agent: AgentData.getAgentById('dermis'),
      imageFile: imageFile,
      description: description,
    );
  }

  static Future<bool> isServerAvailable() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {
          'accept': 'application/json; charset=utf-8',
        },
      ).timeout(const Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  static Future<List<Clinic>> getNearbyClinics({
    required double lat,
    required double lon,
    double radio = 3000,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/google/clinicas_cercanas?lat=$lat&lon=$lon&radio=$radio'),
        headers: {
          'accept': 'application/json; charset=utf-8',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(utf8.decode(response.bodyBytes));
        return jsonList.map((json) => Clinic.fromJson(json)).toList();
      } else {
        throw Exception('Error en la petición: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
} 