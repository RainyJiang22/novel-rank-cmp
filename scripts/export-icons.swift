#!/usr/bin/env swift
// Export the editable SVG to native app-icon assets using macOS AppKit; no app build or dependencies.
import AppKit
import Foundation
import ImageIO

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let files = FileManager.default
let svg = try String(contentsOf: root.appendingPathComponent("assets/branding/app-icon.svg"), encoding: .utf8)
let backgroundPattern = try NSRegularExpression(pattern: #"<rect id="background" width="108" height="108" fill="(#[0-9A-Fa-f]{6})"/>"#)
guard let background = backgroundPattern.firstMatch(in: svg, range: NSRange(svg.startIndex..., in: svg)) else {
    fatalError("Expected a full-bleed RGB background rectangle in app-icon.svg")
}
let backgroundColor = String(svg[Range(background.range(at: 1), in: svg)!])
let desktopSVG = svg.replacingCharacters(in: Range(background.range, in: svg)!,
    with: "<rect x=\"8\" y=\"8\" width=\"92\" height=\"92\" rx=\"20\" fill=\"\(backgroundColor)\"/>")

func write(_ data: Data, _ path: String) throws {
    let url = root.appendingPathComponent(path)
    try files.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
    try data.write(to: url, options: .atomic)
}

try write(Data("""
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">\(backgroundColor)</color>
</resources>

""".utf8), "androidApp/src/main/res/values/colors.xml")

func png(_ artwork: String, size: Int, opaque: Bool) -> Data {
    let image = NSImage(data: Data(artwork.utf8))!
    let alpha = opaque ? CGImageAlphaInfo.noneSkipLast : CGImageAlphaInfo.premultipliedLast
    let bitmap = CGContext(data: nil, width: size, height: size, bitsPerComponent: 8, bytesPerRow: size * 4,
        space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: alpha.rawValue)!
    let context = NSGraphicsContext(cgContext: bitmap, flipped: false)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = context
    context.imageInterpolation = .high
    context.cgContext.clear(CGRect(x: 0, y: 0, width: size, height: size))
    image.draw(in: NSRect(x: 0, y: 0, width: size, height: size),
               from: .zero, operation: .copy, fraction: 1)
    NSGraphicsContext.restoreGraphicsState()
    let data = NSMutableData()
    let output = CGImageDestinationCreateWithData(data, "public.png" as CFString, 1, nil)!
    CGImageDestinationAddImage(output, bitmap.makeImage()!, nil)
    precondition(CGImageDestinationFinalize(output), "PNG export failed")
    return data as Data
}

// Android uses the same paths. The small foreground transform keeps the mark inside the safe zone.
final class Paths: NSObject, XMLParserDelegate {
    var values: [(fill: String, path: String)] = []
    func parser(_ parser: XMLParser, didStartElement elementName: String, namespaceURI: String?,
                qualifiedName: String?, attributes: [String: String]) {
        if elementName == "path" { values.append((attributes["fill"]!, attributes["d"]!)) }
    }
}
let parser = XMLParser(data: Data(svg.utf8))
let paths = Paths()
parser.delegate = paths
precondition(parser.parse() && paths.values.count == 8 && svg.contains("transform=\"translate(0 6)\""),
    "Expected two pages, two text cuts, three bars and an arrow in app-icon.svg")
func vector(_ body: String) -> Data {
    Data("""
    <?xml version="1.0" encoding="utf-8"?>
    <!-- Generated from assets/branding/app-icon.svg by scripts/export-icons.swift. -->
    <vector xmlns:android="http://schemas.android.com/apk/res/android"
        android:width="108dp" android:height="108dp"
        android:viewportWidth="108" android:viewportHeight="108">
        <group android:pivotX="54" android:pivotY="54" android:scaleX="0.82" android:scaleY="0.82" android:translateY="4.92">
    \(body)
        </group>
    </vector>

    """.utf8)
}
let foreground = paths.values.map { "        <path android:fillColor=\"\($0.fill)\" android:pathData=\"\($0.path)\" />" }.joined(separator: "\n")
try write(vector(foreground), "androidApp/src/main/res/drawable/ic_launcher_foreground.xml")
let monochrome = [[0, 2, 3], [1, 4, 5, 6], [7]].map { indices in
    let path = indices.map { paths.values[$0].path }.joined(separator: " ")
    return "        <path android:fillColor=\"#FFFFFF\" android:fillType=\"evenOdd\" android:pathData=\"\(path)\" />"
}.joined(separator: "\n")
try write(vector(monochrome), "androidApp/src/main/res/drawable/ic_launcher_monochrome.xml")

func json(_ object: Any, _ path: String) throws {
    var data = try JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    data.append(10)
    try write(data, path)
}

// iOS uses full-bleed RGB images without a baked-in corner mask or alpha channel.
let catalog = "iosApp/iosApp/Assets.xcassets"
let info: [String: Any] = ["author": "xcode", "version": 1]
try json(["info": info], "\(catalog)/Contents.json")
var images: [[String: String]] = []
var renderedSizes = Set<Int>()
for (idiom, points, scales) in [
    ("iphone", "20", [2, 3]), ("iphone", "29", [2, 3]),
    ("iphone", "40", [2, 3]), ("iphone", "60", [2, 3]),
    ("ipad", "20", [1, 2]), ("ipad", "29", [1, 2]),
    ("ipad", "40", [1, 2]), ("ipad", "76", [1, 2]),
    ("ipad", "83.5", [2]), ("ios-marketing", "1024", [1]),
] {
    for scale in scales {
        let pixels = Int(Double(points)! * Double(scale))
        let name = "AppIcon-\(pixels).png"
        if renderedSizes.insert(pixels).inserted {
            try write(png(svg, size: pixels, opaque: true), "\(catalog)/AppIcon.appiconset/\(name)")
        }
        images.append(["idiom": idiom, "size": "\(points)x\(points)", "scale": "\(scale)x", "filename": name])
    }
}
try json(["info": info, "images": images], "\(catalog)/AppIcon.appiconset/Contents.json")
try write(png(svg, size: 1024, opaque: true), "assets/branding/app-icon.png")
try write(png(desktopSVG, size: 512, opaque: false), "composeApp/src/desktopMain/resources/icons/app-icon.png")

// macOS ICNS contains native-resolution representations from 16 px through 1024 px.
let iconset = files.temporaryDirectory.appendingPathComponent("novelrank-\(UUID().uuidString).iconset")
try files.createDirectory(at: iconset, withIntermediateDirectories: true)
defer { try? files.removeItem(at: iconset) }
for size in [16, 32, 128, 256, 512] {
    for scale in [1, 2] {
        let suffix = scale == 2 ? "@2x" : ""
        try png(desktopSVG, size: size * scale, opaque: false).write(
            to: iconset.appendingPathComponent("icon_\(size)x\(size)\(suffix).png"))
    }
}
let iconutil = Process()
iconutil.executableURL = URL(fileURLWithPath: "/usr/bin/iconutil")
iconutil.arguments = ["-c", "icns", iconset.path, "-o", root.appendingPathComponent("assets/branding/app-icon.icns").path]
try iconutil.run()
iconutil.waitUntilExit()
precondition(iconutil.terminationStatus == 0, "iconutil failed")

// ICO directory entries point to lossless PNG frames, supported by modern Windows.
func little<T: FixedWidthInteger>(_ value: T) -> Data {
    var value = value.littleEndian
    return withUnsafeBytes(of: &value) { Data($0) }
}
let sizes = [16, 32, 48, 64, 128, 256]
let frames = sizes.map { png(desktopSVG, size: $0, opaque: false) }
var ico = little(UInt16(0)) + little(UInt16(1)) + little(UInt16(sizes.count))
var offset = 6 + 16 * sizes.count
for (size, frame) in zip(sizes, frames) {
    ico.append(contentsOf: [UInt8(size % 256), UInt8(size % 256), 0, 0])
    ico.append(little(UInt16(1)))
    ico.append(little(UInt16(32)))
    ico.append(little(UInt32(frame.count)))
    ico.append(little(UInt32(offset)))
    offset += frame.count
}
for frame in frames { ico.append(frame) }
try write(ico, "assets/branding/app-icon.ico")
print("Exported Android vectors, \(images.count) iOS slots (\(renderedSizes.count) RGB PNGs), desktop PNG, ICNS and ICO.")
