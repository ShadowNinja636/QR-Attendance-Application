import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'package:vibration/vibration.dart';

void main() {
  runApp(const MyApp());
}

const String baseUrl = "http://10.31.232.42:8000";

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: QRScannerScreen(),
    );
  }
}

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  bool isProcessing = false;
  String statusMessage = "Ready to Scan";
  Color statusColor = Colors.blue;

  int attendanceCount = 0;

  final MobileScannerController cameraController = MobileScannerController();

  @override
  void initState() {
    super.initState();
    fetchAttendanceCount();
  }

  Future<void> vibrateSuccess() async {
    if (await Vibration.hasVibrator() ?? false) {
      Vibration.vibrate(duration: 120);
    }
  }

  Future<void> sendAttendance(String qrId) async {
    setState(() {
      isProcessing = true;
      statusMessage = "Processing...";
      statusColor = Colors.blue;
    });

    try {
      final response = await http.post(
        Uri.parse("$baseUrl/attendance/scan"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "qr_id": qrId,
          "session_id": "SUNDAY_SERVICE"
        }),
      );

      final data = jsonDecode(response.body);
      final message = data["message"] ?? "Unknown response";

      if (message.toLowerCase().contains("already")) {
        statusColor = Colors.orange;
      } else if (message.toLowerCase().contains("success") ||
          message.toLowerCase().contains("recorded")) {
        statusColor = Colors.green;
        await vibrateSuccess();
      } else {
        statusColor = Colors.red;
      }

      setState(() {
        statusMessage = message;
      });

      if (message.toLowerCase().contains("already") ||
          message.toLowerCase().contains("success") ||
          message.toLowerCase().contains("recorded")) {
        await fetchAttendanceCount();
      }
    } catch (e) {
      setState(() {
        statusMessage = "Connection Error";
        statusColor = Colors.red;
      });
    }

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      isProcessing = false;
      statusMessage = "Ready to Scan";
      statusColor = Colors.blue;
    });
  }

  Future<void> downloadTodayAttendance() async {
    final today = DateTime.now();

    final formatted =
        "${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}";

    final url = Uri.parse("$baseUrl/attendance/export?date=$formatted");

    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception("Could not open attendance download");
    }
  }

  Future<void> downloadQrSheet() async {
    final url = Uri.parse("$baseUrl/qr/print-sheet");

    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception("Could not open QR sheet");
    }
  }

  Future<void> fetchAttendanceCount() async {
    try {
      final response =
          await http.get(Uri.parse("$baseUrl/attendance/count/today"));

      final data = jsonDecode(response.body);

      setState(() {
        attendanceCount = data["count"];
      });
    } catch (e) {
      debugPrint("Failed to fetch attendance count");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("QR Attendance Scanner"),
        backgroundColor: Colors.black,
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: cameraController,
            onDetect: (barcodeCapture) {
              if (isProcessing) return;

              final barcode = barcodeCapture.barcodes.first;
              final qrId = barcode.rawValue;

              if (qrId != null) {
                sendAttendance(qrId);
              }
            },
          ),

          // Attendance Counter
          Align(
            alignment: Alignment.topCenter,
            child: Padding(
              padding: const EdgeInsets.only(top: 20),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                decoration: BoxDecoration(
                  color: Colors.black87,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  "Today's Attendance: $attendanceCount",
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),

          // Scan Box
          Center(
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white, width: 3),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),

          // Buttons
          Align(
            alignment: Alignment.bottomCenter,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 80),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton.icon(
                    onPressed: downloadTodayAttendance,
                    icon: const Icon(Icons.download),
                    label: const Text("Attendance"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                  ),
                  ElevatedButton.icon(
                    onPressed: downloadQrSheet,
                    icon: const Icon(Icons.qr_code),
                    label: const Text("QR Sheet"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Status Banner
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: statusColor,
              child: Text(
                statusMessage,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}