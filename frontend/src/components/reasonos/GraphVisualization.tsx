import { instance } from '@viz-js/viz';
import React, { useEffect, useRef, useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2, Minimize2, RotateCcw, Download } from 'lucide-react';
import { reasonosAPI } from '../../services/reasonos-api';

interface GraphVisualizationProps {
  repoPath: string;
  maxNodes?: number;
  focusFunction?: string;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  repoPath,
  maxNodes = 100,
  focusFunction,
}) => {
  const [svgContent, setSvgContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<any>(null);
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadGraph();
  }, [repoPath, maxNodes, focusFunction]);

  const loadGraph = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch DOT format from backend
      const dotData = await reasonosAPI.exportGraphDOT(repoPath, maxNodes, focusFunction);
      setMetadata(dotData.metadata);

      // Render DOT to SVG using viz.js
      const viz = await instance();
      const svg = viz.renderSVGElement(dotData.content);

      // Convert SVG element to string
      const svgString = new XMLSerializer().serializeToString(svg);
      setSvgContent(svgString);
    } catch (err: any) {
      setError(err.message || 'Failed to load graph');
      console.error('Graph loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleResetZoom = () => setZoom(1);
  const toggleFullscreen = () => setIsFullscreen(prev => !prev);

  const handleDownloadDOT = async () => {
    try {
      const dotData = await reasonosAPI.exportGraphDOT(repoPath, maxNodes, focusFunction);

      // Create a blob from the DOT content
      const blob = new Blob([dotData.content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);

      // Create a temporary download link
      const a = document.createElement('a');
      a.href = url;
      a.download = `dependency-graph-${new Date().getTime()}.dot`;
      document.body.appendChild(a);
      a.click();

      // Cleanup
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Download failed:', err);
      alert('Failed to download DOT file: ' + err.message);
    }
  };

  const handleDownloadSVG = () => {
    try {
      if (!svgContent) return;

      // Create a blob from the SVG content
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);

      // Create a temporary download link
      const a = document.createElement('a');
      a.href = url;
      a.download = `dependency-graph-${new Date().getTime()}.svg`;
      document.body.appendChild(a);
      a.click();

      // Cleanup
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('SVG download failed:', err);
      alert('Failed to download SVG file: ' + err.message);
    }
  };  return (
    <div className={`bg-[#101010] rounded-lg border border-gray-800 transition-all ${
      isFullscreen ? 'fixed inset-4 z-50 p-6' : 'p-4 md:p-6'
    }`}>
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div className="flex-1">
          <h3 className="text-lg md:text-xl font-semibold text-white">
            Dependency Graph
          </h3>
          {metadata && (
            <p className="text-xs md:text-sm text-gray-400 mt-1">
              Showing {metadata.max_nodes} of {metadata.total_nodes} nodes
              {focusFunction && ` (focused on: ${focusFunction})`}
            </p>
          )}
        </div>

        {/* Control buttons */}
        <div className="flex gap-2 flex-wrap">
          <div className="flex gap-1 bg-[#1a1a1a] rounded-lg p-1">
            <button
              onClick={handleZoomOut}
              disabled={loading || zoom <= 0.5}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              disabled={loading}
              className="px-3 py-2 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 transition-colors"
              title="Reset Zoom"
            >
              {Math.round(zoom * 100)}%
            </button>
            <button
              onClick={handleZoomIn}
              disabled={loading || zoom >= 3}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>

          <button
            onClick={toggleFullscreen}
            disabled={loading}
            className="p-2 bg-[#1a1a1a] text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg disabled:opacity-30 transition-colors"
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          <div className="flex gap-1 bg-[#1a1a1a] rounded-lg p-1">
            <button
              onClick={handleDownloadDOT}
              disabled={loading || !svgContent}
              className="px-3 py-2 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              title="Download as DOT format (for Graphviz)"
            >
              <Download className="w-3 h-3" />
              <span className="hidden md:inline">DOT</span>
            </button>
            <button
              onClick={handleDownloadSVG}
              disabled={loading || !svgContent}
              className="px-3 py-2 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              title="Download as SVG image"
            >
              <Download className="w-3 h-3" />
              <span className="hidden md:inline">SVG</span>
            </button>
          </div>

          <button
            onClick={loadGraph}
            disabled={loading}
            className="px-3 py-2 bg-[#2997FF] text-white text-sm rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            <RotateCcw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">{loading ? 'Loading...' : 'Refresh'}</span>
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64 md:h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#2997FF] mx-auto mb-4"></div>
            <p className="text-gray-400 text-sm">Loading graph...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4 text-red-400">
          <p className="font-medium">Error loading graph:</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {!loading && !error && svgContent && (
        <div
          ref={containerRef}
          className="overflow-auto bg-white rounded-lg border border-gray-300 shadow-lg"
          style={{
            height: isFullscreen ? 'calc(100vh - 180px)' : 'auto',
            maxHeight: isFullscreen ? 'none' : '70vh',
            minHeight: '400px'
          }}
        >
          <div
            ref={svgRef}
            dangerouslySetInnerHTML={{ __html: svgContent }}
            className="p-2 md:p-4 transition-transform origin-top-left"
            style={{
              transform: `scale(${zoom})`,
              minWidth: 'fit-content'
            }}
          />
        </div>
      )}

      {!loading && !error && !svgContent && (
        <div className="text-center text-gray-400 py-12 md:py-16">
          <p className="text-lg">No graph data available</p>
          <p className="text-sm mt-2">Try analyzing the repository first</p>
        </div>
      )}
    </div>
  );
};
