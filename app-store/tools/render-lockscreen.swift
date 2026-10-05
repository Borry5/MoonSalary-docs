import SwiftUI
import AppKit

// 渲染 iOS 锁屏 + accessoryRectangular 小组件（1320×2868）
// 小组件文案/字体/字重严格照搬 MoonWidget/IncomeWidget.swift 的 lockScreenView：
//   .font(.system(size: 24, weight: .heavy, design: .rounded)) + monospacedDigit + 白色

_ = NSApplication.shared

let W: CGFloat = 440      // iPhone 17 Pro Max 逻辑宽
let H: CGFloat = 956      // 逻辑高
let SCALE: CGFloat = 3    // 出图 1320×2868

struct LockScreenView: View {
    let amount: String
    let dateText: String
    let timeText: String

    var body: some View {
        ZStack {
            wallpaper
            content
        }
        .frame(width: W, height: H)
        .clipped()
    }

    private var wallpaper: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.04, green: 0.06, blue: 0.13),
                    Color(red: 0.07, green: 0.10, blue: 0.20),
                    Color(red: 0.10, green: 0.09, blue: 0.16),
                    Color(red: 0.03, green: 0.04, blue: 0.09)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            RadialGradient(
                colors: [Color(red: 1.0, green: 0.70, blue: 0.18).opacity(0.46), .clear],
                center: UnitPoint(x: 0.80, y: 0.16),
                startRadius: 0, endRadius: 290
            )
            RadialGradient(
                colors: [Color(red: 0.20, green: 0.36, blue: 0.95).opacity(0.30), .clear],
                center: UnitPoint(x: 0.14, y: 0.60),
                startRadius: 0, endRadius: 300
            )
            RadialGradient(
                colors: [Color(red: 0.95, green: 0.45, blue: 0.15).opacity(0.20), .clear],
                center: UnitPoint(x: 0.30, y: 0.98),
                startRadius: 0, endRadius: 340
            )
        }
    }

    private var content: some View {
        VStack(spacing: 0) {
            Spacer().frame(height: 84)

            Text(dateText)
                .font(.system(size: 17, weight: .semibold))
                .foregroundColor(.white.opacity(0.96))

            Text(timeText)
                .font(.system(size: 94, weight: .medium))
                .foregroundColor(.white)
                .monospacedDigit()
                .padding(.top, -2)

            Spacer().frame(height: 14)

            widgetRow

            Spacer()

            bottomButtons
            Spacer().frame(height: 44)
        }
    }

    // accessoryRectangular：锁屏矩形小组件
    private var widgetRow: some View {
        VStack(alignment: .center, spacing: 2) {
            HStack(spacing: 6) {
                Text(amount)
                    .font(.system(size: 24, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
                    .monospacedDigit()
                    .lineLimit(1)
                    .minimumScaleFactor(0.55)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
        .frame(width: 158, height: 72)
        .shadow(color: .black.opacity(0.35), radius: 6, x: 0, y: 1)
    }

    private var bottomButtons: some View {
        HStack {
            circleButton(systemName: "flashlight.on.fill")
            Spacer()
            circleButton(systemName: "camera.fill")
        }
        .padding(.horizontal, 52)
    }

    private func circleButton(systemName: String) -> some View {
        ZStack {
            Circle().fill(Color.white.opacity(0.18))
            Image(systemName: systemName)
                .font(.system(size: 20, weight: .medium))
                .foregroundColor(.white)
        }
        .frame(width: 48, height: 48)
    }
}

@MainActor
func render() {
    let view = LockScreenView(amount: "¥628.2", dateText: "10月6日 星期二", timeText: "9:41")
    let renderer = ImageRenderer(content: view)
    renderer.scale = SCALE
    renderer.isOpaque = true

    guard let nsImage = renderer.nsImage,
          let tiff = nsImage.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else {
        FileHandle.standardError.write("render failed\n".data(using: .utf8)!)
        exit(1)
    }

    let out = CommandLine.arguments.count > 1
        ? CommandLine.arguments[1]
        : "/tmp/msrender-lock/lockscreen.png"
    do {
        try png.write(to: URL(fileURLWithPath: out))
        print("OK \(out) \(rep.pixelsWide)x\(rep.pixelsHigh)")
    } catch {
        FileHandle.standardError.write("write failed: \(error)\n".data(using: .utf8)!)
        exit(1)
    }
}

MainActor.assumeIsolated { render() }
