import SwiftUI
import AppKit

// macOS 面板离屏渲染。
//
// 两条路都留着，因为各有各的坑：
//
//  A. ImageRenderer —— 干净、能直接控 scale、不撞入场动画，
//     但渲染不了 TextField（渲成黄底 🚫 方块）。适合无输入框的面板。
//
//  B. NSHostingView + cacheDisplay —— TextField 能正常渲染，
//     但会撞上视图 onAppear 里的 withAnimation，截到动画中途的半透明重影。
//     解法：渲染前先跑 RunLoop 让动画自然跑完（settle 秒）。
//
// 用法：render <outDir> [settleSeconds]

_ = NSApplication.shared

@MainActor
func writePNG(_ rep: NSBitmapImageRep, to path: String) {
    guard let png = rep.representation(using: .png, properties: [:]) else {
        FileHandle.standardError.write("png encode failed: \(path)\n".data(using: .utf8)!)
        return
    }
    do {
        try png.write(to: URL(fileURLWithPath: path))
        print("OK \(path) \(rep.pixelsWide)x\(rep.pixelsHigh)")
    } catch {
        FileHandle.standardError.write("write failed \(path): \(error)\n".data(using: .utf8)!)
    }
}

/// A 路：ImageRenderer。scale 直接控倍率，无动画干扰，但渲不了 TextField。
@MainActor
func renderImage<V: View>(_ view: V, width: CGFloat, scale: CGFloat, to path: String) {
    let renderer = ImageRenderer(content: view.frame(width: width))
    renderer.scale = scale
    renderer.isOpaque = false

    guard let nsImage = renderer.nsImage,
          let tiff = nsImage.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff) else {
        FileHandle.standardError.write("render failed: \(path)\n".data(using: .utf8)!)
        return
    }
    writePNG(rep, to: path)
}

/// B 路：NSHostingView + cacheDisplay，渲染前跑 RunLoop 等入场动画结束。
@MainActor
func renderHosted<V: View>(_ view: V, width: CGFloat, scale: CGFloat,
                           settle: TimeInterval, to path: String) {
    let host = NSHostingView(rootView: view)
    // 关键：脱离窗口的 NSHostingView 解析不出 effectiveAppearance，
    // 动态色（.primary/.secondary）会按深色外观取值 —— 浅色文字贴白底 = 看不见。
    // 必须显式钉成 aqua，与 App Store 展示图要求的浅色底一致。
    host.appearance = NSAppearance(named: .aqua)

    // 先给个占位高度，量出真实内容高度
    host.frame = NSRect(x: 0, y: 0, width: width, height: 10)
    host.layoutSubtreeIfNeeded()
    let fit = host.fittingSize
    host.frame = NSRect(x: 0, y: 0, width: width, height: max(fit.height, 10))
    host.layoutSubtreeIfNeeded()

    // 关键：把 onAppear 里的 withAnimation 跑完，否则截到半透明重影
    let end = Date().addingTimeInterval(settle)
    while Date() < end {
        RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.02))
    }
    host.layoutSubtreeIfNeeded()
    host.displayIfNeeded()

    let pxW = Int((host.bounds.width * scale).rounded())
    let pxH = Int((host.bounds.height * scale).rounded())
    guard let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: pxW, pixelsHigh: pxH,
        bitsPerSample: 8, samplesPerPixel: 4,
        hasAlpha: true, isPlanar: false,
        colorSpaceName: .deviceRGB,
        bytesPerRow: 0, bitsPerPixel: 0
    ) else {
        FileHandle.standardError.write("rep alloc failed: \(path)\n".data(using: .utf8)!)
        return
    }
    // rep.size = 逻辑尺寸 → cacheDisplay 按 scale 倍绘制
    rep.size = host.bounds.size
    host.cacheDisplay(in: host.bounds, to: rep)
    writePNG(rep, to: path)
}

MainActor.assumeIsolated {
    let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "/tmp/msrender-mac"
    let settle = CommandLine.arguments.count > 2 ? (Double(CommandLine.arguments[2]) ?? 1.2) : 1.2

    let store = IncomeStore.shared

    // 设置面板含 TextField（月/日/时收入三栏），走 B 路。
    // 它自身不画背景 —— 真实场景里靠菜单栏面板的 NSVisualEffectView 材质层，
    // 离屏渲染时那层渲不出来，结果是全透明，合成到浅色底上会变成黑块。
    // 手动补上 #F2F2F7（与主面板渲染出的底色、真实截图里的面板底色一致）
    renderHosted(
        SettingsPanelView(store: store)
            .background(Color(red: 242 / 255, green: 242 / 255, blue: 247 / 255)),
        width: 300, scale: 2, settle: settle, to: "\(out)/settings.png"
    )

    // 主面板无输入框，A 路更干净；顺带留一张做对照
    renderImage(MainPanelView(store: store), width: 300, scale: 2,
                to: "\(out)/panel-image.png")
    renderHosted(MainPanelView(store: store), width: 300, scale: 2,
                 settle: settle, to: "\(out)/panel-hosted.png")
}
