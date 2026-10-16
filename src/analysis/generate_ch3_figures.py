#!/usr/bin/env python3
"""generate_ch3_figures.py
Generates publication-grade, 300-DPI architectural diagrams for Chapter 3:
1. Figure 3.1: Four-Tier End-to-End System Architecture Block Diagram
2. Figure 3.2: Priority Arbitration State Machine and Dwell-Time Safety Flowchart
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

OUT_DIR = "results/figures"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_fig_3_1():
    """Generates Figure 3.1: Four-Tier End-to-End System Architecture Block Diagram"""
    fig, ax = plt.subplots(figsize=(13, 8), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(6.5, 7.6, "FOUR-TIER EMBEDDED SYSTEM ARCHITECTURE FOR CROSS-LIMB NEUROREHABILITATION",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#002060')

    # Color Palette
    c_tier1 = '#E8F4F8' # Pale Cyan
    b_tier1 = '#1B4965' # Deep Cyan
    c_tier2 = '#EBF5FB' # Pale Blue
    b_tier2 = '#1A5276' # Navy
    c_tier3 = '#FEF9E7' # Pale Amber
    b_tier3 = '#B7950B' # Dark Amber
    c_tier4 = '#EAFAF1' # Pale Green
    b_tier4 = '#1E8449' # Forest Green

    # Tier 1 Container
    rect1 = patches.FancyBboxPatch((0.5, 0.5), 2.6, 6.7, boxstyle="round,pad=0.1,rounding_size=0.15",
                                   facecolor=c_tier1, edgecolor=b_tier1, linewidth=1.8)
    ax.add_patch(rect1)
    ax.text(1.8, 6.9, "TIER 1: BIOSIGNAL ACQUISITION", ha='center', va='center', fontsize=9, fontweight='bold', color=b_tier1)

    # Tier 1 Sub-blocks
    # Sub-block 1A: cEEGrid
    sb1a = patches.FancyBboxPatch((0.7, 5.0), 2.2, 1.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier1, linewidth=1.2)
    ax.add_patch(sb1a)
    ax.text(1.8, 6.2, "OpenBCI cEEGrid", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(1.8, 5.8, "• 16 Around-Ear Leads\n• TI ADS1299 (24-bit)\n• Fs = 250 Hz (BLE/USB)",
            ha='center', va='center', fontsize=7.5, color='#333')

    # Sub-block 1B: Qneuro H100
    sb1b = patches.FancyBboxPatch((0.7, 3.1), 2.2, 1.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier1, linewidth=1.2)
    ax.add_patch(sb1b)
    ax.text(1.8, 4.3, "Qneuro H100 Headset", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(1.8, 3.9, "• 8-ch EEG + 2-ch PPG\n• Wireless BT SPP\n• Fs = 250 Hz (LSL)",
            ha='center', va='center', fontsize=7.5, color='#333')

    # Sub-block 1C: Buffer
    sb1c = patches.FancyBboxPatch((0.7, 0.9), 2.2, 1.9, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier1, linewidth=1.2)
    ax.add_patch(sb1c)
    ax.text(1.8, 2.4, "Circular Ring Buffer", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(1.8, 1.7, "• Mutex Protected\n• 2000 Sample Capacity\n• 2.0s Window (500 pts)\n• 100 ms Step (25 pts)",
            ha='center', va='center', fontsize=7.5, color='#333')

    # Connectors within Tier 1
    ax.annotate('', xy=(1.8, 5.0), xytext=(1.8, 4.7), arrowprops=dict(arrowstyle="->", color=b_tier1, lw=1.2))
    ax.annotate('', xy=(1.8, 3.1), xytext=(1.8, 2.8), arrowprops=dict(arrowstyle="->", color=b_tier1, lw=1.2))

    # Tier 2 Container
    rect2 = patches.FancyBboxPatch((3.5, 0.5), 3.5, 6.7, boxstyle="round,pad=0.1,rounding_size=0.15",
                                   facecolor=c_tier2, edgecolor=b_tier2, linewidth=1.8)
    ax.add_patch(rect2)
    ax.text(5.25, 6.9, "TIER 2: EDGE AI HOST (Jetson Orin Nano)", ha='center', va='center', fontsize=9, fontweight='bold', color=b_tier2)

    # Tier 2 Sub-blocks
    # Filter
    sb2a = patches.FancyBboxPatch((3.7, 5.6), 3.1, 1.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier2, linewidth=1.2)
    ax.add_patch(sb2a)
    ax.text(5.25, 6.2, "Zero-Phase Filter Pipeline", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(5.25, 5.85, "4th-ord Butterworth (0.5-45 Hz) + 50Hz Notch (Q=30)", ha='center', va='center', fontsize=7, color='#333')

    # Features
    sb2b = patches.FancyBboxPatch((3.7, 3.7), 3.1, 1.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier2, linewidth=1.2)
    ax.add_patch(sb2b)
    ax.text(5.25, 4.95, "Four Parallel Feature Extractors", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(5.25, 4.3, "• L1 Veto: Differential EOG Peak (>40 µV)\n• L2 EMG: Temporalis High-Gamma Log-Var\n• L2.5 MI: Sensorimotor Mu/Beta (8-30 Hz) ERD\n• L3 ERP: 250-500 ms P300 Oddball Window\n• L4 Workload: Alpha Ratio (8-13 Hz)",
            ha='center', va='center', fontsize=6.8, color='#333')

    # Classifiers
    sb2c = patches.FancyBboxPatch((3.7, 2.3), 3.1, 1.1, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier2, linewidth=1.2)
    ax.add_patch(sb2c)
    ax.text(5.25, 3.0, "Real-Time Classifiers", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#111')
    ax.text(5.25, 2.6, "• SWLDA Sparse Linear Inference (w·x + b)\n• Workload LDA + Movement Random Forest", ha='center', va='center', fontsize=7, color='#333')

    # Arbitrator
    sb2d = patches.FancyBboxPatch((3.7, 0.8), 3.1, 1.2, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='#FADBD8', edgecolor='#C0392B', linewidth=1.5)
    ax.add_patch(sb2d)
    ax.text(5.25, 1.65, "Stateful Priority Arbitrator", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#900C3F')
    ax.text(5.25, 1.2, "• 5-Tier Priority Cascade (L1 E-Stop -> L4 Rest)\n• 300 ms Dwell Gate & 500 ms Veto Lockout", ha='center', va='center', fontsize=7, color='#78281F')

    # Arrows inside Tier 2
    ax.annotate('', xy=(5.25, 5.6), xytext=(5.25, 5.3), arrowprops=dict(arrowstyle="->", color=b_tier2, lw=1.2))
    ax.annotate('', xy=(5.25, 3.7), xytext=(5.25, 3.4), arrowprops=dict(arrowstyle="->", color=b_tier2, lw=1.2))
    ax.annotate('', xy=(5.25, 2.3), xytext=(5.25, 2.0), arrowprops=dict(arrowstyle="->", color=b_tier2, lw=1.2))

    # Connector Tier 1 -> Tier 2
    ax.annotate('', xy=(3.5, 6.1), xytext=(2.9, 1.8),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.25", color=b_tier2, lw=2.0))
    ax.text(3.1, 4.4, "250 Hz Ring\nSamples", ha='center', va='center', fontsize=7.5, fontweight='bold', color=b_tier2, rotation=90)

    # Tier 3 Container
    rect3 = patches.FancyBboxPatch((7.4, 0.5), 2.5, 6.7, boxstyle="round,pad=0.1,rounding_size=0.15",
                                   facecolor=c_tier3, edgecolor=b_tier3, linewidth=1.8)
    ax.add_patch(rect3)
    ax.text(8.65, 6.9, "TIER 3: EMBEDDED MCU", ha='center', va='center', fontsize=9, fontweight='bold', color=b_tier3)
    ax.text(8.65, 6.65, "(ESP32-P4 Dual-Core RISC-V)", ha='center', va='center', fontsize=7.5, color='#555')

    # Tier 3 Sub-blocks
    sb3a = patches.FancyBboxPatch((7.6, 5.1), 2.1, 1.3, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier3, linewidth=1.2)
    ax.add_patch(sb3a)
    ax.text(8.65, 5.9, "Binary UART Parser", ha='center', va='center', fontsize=8, fontweight='bold', color='#111')
    ax.text(8.65, 5.45, "• 115200 Baud Interrupt\n• 7-Byte Strict Frame\n• CRC-8/MAXIM Verify", ha='center', va='center', fontsize=7, color='#333')

    sb3b = patches.FancyBboxPatch((7.6, 2.8), 2.1, 2.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier3, linewidth=1.2)
    ax.add_patch(sb3b)
    ax.text(8.65, 4.4, "FreeRTOS Scheduler", ha='center', va='center', fontsize=8, fontweight='bold', color='#111')
    ax.text(8.65, 3.6, "• task_safety (Core 0, P6)\n• task_uart (Core 0, P5)\n• task_motor (Core 1, P3)\n• task_heartbeat (P1)", ha='center', va='center', fontsize=7, color='#333')

    sb3c = patches.FancyBboxPatch((7.6, 0.8), 2.1, 1.7, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier3, linewidth=1.2)
    ax.add_patch(sb3c)
    ax.text(8.65, 2.1, "Motion Profiler", ha='center', va='center', fontsize=8, fontweight='bold', color='#111')
    ax.text(8.65, 1.45, "• Trapezoidal Profile\n• PCA9685 I2C (12-bit)\n• PWM Dual H-Bridge\n• Soft-Start / Hard-Stop", ha='center', va='center', fontsize=7, color='#333')

    # Connectors within Tier 3
    ax.annotate('', xy=(8.65, 5.1), xytext=(8.65, 4.8), arrowprops=dict(arrowstyle="->", color=b_tier3, lw=1.2))
    ax.annotate('', xy=(8.65, 2.8), xytext=(8.65, 2.5), arrowprops=dict(arrowstyle="->", color=b_tier3, lw=1.2))

    # Connector Tier 2 -> Tier 3
    ax.annotate('', xy=(7.4, 1.4), xytext=(6.8, 1.4),
                arrowprops=dict(arrowstyle="->", color='#C0392B', lw=2.5))
    ax.text(7.1, 1.7, "7-Byte\nPacket", ha='center', va='center', fontsize=7, fontweight='bold', color='#C0392B')

    # Tier 4 Container
    rect4 = patches.FancyBboxPatch((10.3, 0.5), 2.3, 6.7, boxstyle="round,pad=0.1,rounding_size=0.15",
                                   facecolor=c_tier4, edgecolor=b_tier4, linewidth=1.8)
    ax.add_patch(rect4)
    ax.text(11.45, 6.9, "TIER 4: PHYSICAL TESTBED", ha='center', va='center', fontsize=9, fontweight='bold', color=b_tier4)
    ax.text(11.45, 6.65, "(Dual Cross-Limb Modules)", ha='center', va='center', fontsize=7.5, color='#555')

    # Tier 4 Sub-blocks
    sb4a = patches.FancyBboxPatch((10.5, 3.8), 1.9, 2.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier4, linewidth=1.2)
    ax.add_patch(sb4a)
    ax.text(11.45, 5.95, "5-DOF Hand Exoskeleton", ha='center', va='center', fontsize=8, fontweight='bold', color='#111')
    ax.text(11.45, 4.9, "• 5x MG996R Servos\n• Bowden Cable Tendons\n• PCA9685 I2C 12-bit PWM\n• Tactile FSR Feedback\n• Open (0x10) / Close (0x20)",
            ha='center', va='center', fontsize=6.8, color='#333')

    sb4b = patches.FancyBboxPatch((10.5, 0.8), 1.9, 2.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                  facecolor='white', edgecolor=b_tier4, linewidth=1.2)
    ax.add_patch(sb4b)
    ax.text(11.45, 2.95, "2-DOF Leg Exoskeleton", ha='center', va='center', fontsize=8, fontweight='bold', color='#111')
    ax.text(11.45, 1.9, "• Dual L298N H-Bridge\n• 12V 50 RPM Planetary\n• Hip/Knee Articulation\n• Hardware Limit Switches\n• Step Fwd (0x30) / Back",
            ha='center', va='center', fontsize=6.8, color='#333')

    # Connectors Tier 3 -> Tier 4
    ax.annotate('', xy=(10.5, 5.0), xytext=(9.7, 1.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.2", color=b_tier4, lw=1.8))
    ax.annotate('', xy=(10.5, 2.0), xytext=(9.7, 1.4),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.05", color=b_tier4, lw=1.8))
    ax.text(10.1, 3.5, "PWM", ha='center', va='center', fontsize=7.5, fontweight='bold', color=b_tier4)

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "fig_3_1_system_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {out_path}")

    # Write companion text file
    with open(os.path.join(OUT_DIR, "fig_3_1_system_architecture.txt"), 'w') as f:
        f.write("Figure 3.1: Four-Tier End-to-End System Architecture Block Diagram\n")
        f.write("Shows Tier 1 (Biosignal Acquisition), Tier 2 (Jetson Edge AI Host), Tier 3 (ESP32-P4 FreeRTOS MCU), and Tier 4 (Physical Hand and Leg Testbed).\n")


def generate_fig_3_2():
    """Generates Figure 3.2: Priority Arbitration State Machine and Dwell-Time Safety Flowchart"""
    fig, ax = plt.subplots(figsize=(11, 8.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Title
    ax.text(5.5, 8.6, "PRIORITY ARBITRATION STATE MACHINE & DWELL-TIME SAFETY FLOWCHART",
            ha='center', va='center', fontsize=11.5, fontweight='bold', color='#900C3F')

    # Start block: Incoming Window
    p_start = patches.FancyBboxPatch((4.0, 7.6), 3.0, 0.7, boxstyle="round,pad=0.08,rounding_size=0.15",
                                     facecolor='#EBF5FB', edgecolor='#2980B9', linewidth=1.5)
    ax.add_patch(p_start)
    ax.text(5.5, 7.95, "New Filtered Biosignal Window\n(2.0s Window, 100 ms Step)",
            ha='center', va='center', fontsize=8, fontweight='bold', color='#1B4965')

    # Arrow down
    ax.annotate('', xy=(5.5, 7.15), xytext=(5.5, 7.6), arrowprops=dict(arrowstyle="->", color='#333', lw=1.5))

    # Priority 1: EOG Veto Decision (Diamond)
    poly_p1 = patches.Polygon([[5.5, 7.15], [7.3, 6.45], [5.5, 5.75], [3.7, 6.45]],
                              facecolor='#FADBD8', edgecolor='#C0392B', linewidth=1.8)
    ax.add_patch(poly_p1)
    ax.text(5.5, 6.45, "Level 1: EOG Double-Blink\nVeto Detected?\n(Peaks > +40 µV, Δt 250-800ms)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#900C3F')

    # Priority 1: YES branch (Emergency Stop)
    ax.annotate('', xy=(8.7, 6.45), xytext=(7.3, 6.45), arrowprops=dict(arrowstyle="->", color='#C0392B', lw=1.8))
    ax.text(7.9, 6.65, "YES", ha='center', va='center', fontsize=8, fontweight='bold', color='#C0392B')

    b_estop = patches.FancyBboxPatch((8.7, 5.95), 2.1, 1.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor='#C0392B', edgecolor='#78281F', linewidth=1.5)
    ax.add_patch(b_estop)
    ax.text(9.75, 6.45, "EMERGENCY HALT (0x99)\nInstant Motor Cutoff\n500 ms Veto Lockout",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='white')

    # Priority 1: NO branch
    ax.annotate('', xy=(5.5, 5.0), xytext=(5.5, 5.75), arrowprops=dict(arrowstyle="->", color='#333', lw=1.5))
    ax.text(5.7, 5.4, "NO", ha='center', va='center', fontsize=8, fontweight='bold', color='#27AE60')

    # Priority 2: Jaw Clench Decision
    poly_p2 = patches.Polygon([[5.5, 5.0], [7.3, 4.3], [5.5, 3.6], [3.7, 4.3]],
                              facecolor='#FCF3CF', edgecolor='#F39C12', linewidth=1.8)
    ax.add_patch(poly_p2)
    ax.text(5.5, 4.3, "Level 2: Temporalis Clench?\n(High-Gamma > +10.5 dB)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#7D6608')

    # Priority 2: YES -> Dwell confirmation
    ax.annotate('', xy=(8.7, 4.3), xytext=(7.3, 4.3), arrowprops=dict(arrowstyle="->", color='#B7950B', lw=1.8))
    ax.text(7.9, 4.5, "YES", ha='center', va='center', fontsize=8, fontweight='bold', color='#B7950B')

    b_dwell_emg = patches.FancyBboxPatch((8.7, 3.8), 2.1, 1.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                                         facecolor='#FEF9E7', edgecolor='#B7950B', linewidth=1.3)
    ax.add_patch(b_dwell_emg)
    ax.text(9.75, 4.3, "300 ms Dwell Met?\n-> Hand Close (0x20)\nElse: Hold / Accumulate",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#7D6608')

    # Priority 2: NO branch
    ax.annotate('', xy=(5.5, 2.9), xytext=(5.5, 3.6), arrowprops=dict(arrowstyle="->", color='#333', lw=1.5))
    ax.text(5.7, 3.25, "NO", ha='center', va='center', fontsize=8, fontweight='bold', color='#27AE60')

    # Priority 2.5: Leg Motor Intent
    poly_p25 = patches.Polygon([[5.5, 2.9], [7.3, 2.2], [5.5, 1.5], [3.7, 2.2]],
                               facecolor='#E8F8F5', edgecolor='#16A085', linewidth=1.8)
    ax.add_patch(poly_p25)
    ax.text(5.5, 2.2, "Level 2.5: Leg Motion Intent?\n(Sensorimotor Mu/Beta ERD)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0E6251')

    # Priority 2.5: YES -> Leg Step
    ax.annotate('', xy=(8.7, 2.2), xytext=(7.3, 2.2), arrowprops=dict(arrowstyle="->", color='#16A085', lw=1.8))
    ax.text(7.9, 2.4, "YES", ha='center', va='center', fontsize=8, fontweight='bold', color='#16A085')

    b_leg = patches.FancyBboxPatch((8.7, 1.7), 2.1, 1.0, boxstyle="round,pad=0.08,rounding_size=0.1",
                                   facecolor='#E8F8F5', edgecolor='#16A085', linewidth=1.3)
    ax.add_patch(b_leg)
    ax.text(9.75, 2.2, "300 ms Dwell Met?\n-> Leg Step Fwd (0x30)\nElse: Hold / Route Leg",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#0E6251')

    # Priority 2.5: NO branch
    ax.annotate('', xy=(5.5, 0.8), xytext=(5.5, 1.5), arrowprops=dict(arrowstyle="->", color='#333', lw=1.5))
    ax.text(5.7, 1.15, "NO", ha='center', va='center', fontsize=8, fontweight='bold', color='#27AE60')

    # Priority 3 / 4 Lower container
    b_p3_p4 = patches.FancyBboxPatch((3.5, 0.1), 4.0, 0.7, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor='#EAF2F8', edgecolor='#2471A3', linewidth=1.5)
    ax.add_patch(b_p3_p4)
    ax.text(5.5, 0.45, "Level 3: P300 Oddball ERP (P >= 0.65 -> Hand Open 0x10)\nLevel 4: Alpha Ratio Fatigue Gate (High Alpha -> Suppress IDLE)",
            ha='center', va='center', fontsize=7.2, fontweight='bold', color='#154360')

    # Common UART Dispatch box on left
    b_uart = patches.FancyBboxPatch((0.4, 2.5), 2.3, 3.5, boxstyle="round,pad=0.1,rounding_size=0.15",
                                    facecolor='#F4F6F6', edgecolor='#34495E', linewidth=1.8)
    ax.add_patch(b_uart)
    ax.text(1.55, 5.6, "UART SERIALIZER", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2C3E50')
    ax.text(1.55, 4.4, "• Frame: 0xAA Header\n• Target Module ID\n• Action Command ID\n• 16-bit Motor Param\n• Confidence Byte\n• CRC-8/MAXIM Check\n• 115200 Baud Tx",
            ha='center', va='center', fontsize=7, color='#2C3E50')
    ax.text(1.55, 2.9, "-> ESP32 FreeRTOS", ha='center', va='center', fontsize=8, fontweight='bold', color='#2980B9')

    # Connect commands to UART Serializer
    ax.annotate('', xy=(2.7, 5.2), xytext=(8.7, 6.45),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.25", color='#C0392B', lw=1.5, ls='--'))
    ax.annotate('', xy=(2.7, 4.3), xytext=(8.7, 4.3),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", color='#B7950B', lw=1.5, ls='--'))
    ax.annotate('', xy=(2.7, 3.4), xytext=(8.7, 2.2),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.15", color='#16A085', lw=1.5, ls='--'))
    ax.annotate('', xy=(2.7, 2.8), xytext=(3.5, 0.45),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.15", color='#2471A3', lw=1.5, ls='--'))

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "fig_3_2_arbitration_flowchart.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {out_path}")

    with open(os.path.join(OUT_DIR, "fig_3_2_arbitration_flowchart.txt"), 'w') as f:
        f.write("Figure 3.2: Priority Arbitration State Machine and Dwell-Time Safety Flowchart\n")
        f.write("Illustrates Level 1 EOG Double-Blink Emergency Veto, Level 2 Temporalis Jaw-Clench, Level 2.5 Leg Intent, Level 3 P300 Oddball, and Level 4 Alpha Workload Fatigue Gating with 300 ms dwell confirmation.\n")

if __name__ == '__main__':
    generate_fig_3_1()
    generate_fig_3_2()
