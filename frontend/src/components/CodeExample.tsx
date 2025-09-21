import { Code, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { CodeExampleProps } from '@/types';

const CodeExample: React.FC<CodeExampleProps> = ({ codeExample, language = 'javascript' }) => {
  const [copiedBefore, setCopiedBefore] = useState(false);
  const [copiedAfter, setCopiedAfter] = useState(false);

  const copyToClipboard = async (text: string, type: 'before' | 'after') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'before') {
        setCopiedBefore(true);
        setTimeout(() => setCopiedBefore(false), 2000);
      } else {
        setCopiedAfter(true);
        setTimeout(() => setCopiedAfter(false), 2000);
      }
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  if (!codeExample.before && !codeExample.after) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2 mb-6">
        <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
          <Code className="w-5 h-5 text-purple-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900">
          Code Example
        </h3>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Before */}
        {codeExample.before && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-red-700 flex items-center space-x-2">
                <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                <span>Before</span>
              </h4>
              <button
                onClick={() => copyToClipboard(codeExample.before, 'before')}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                title="Copy code"
              >
                {copiedBefore ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
            <div className="relative">
              <pre className="code-block scrollbar-thin">
                <code className={`language-${language}`}>
                  {codeExample.before}
                </code>
              </pre>
            </div>
          </div>
        )}

        {/* After */}
        {codeExample.after && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-green-700 flex items-center space-x-2">
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span>After</span>
              </h4>
              <button
                onClick={() => copyToClipboard(codeExample.after, 'after')}
                className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                title="Copy code"
              >
                {copiedAfter ? (
                  <Check className="w-4 h-4 text-green-600" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
            </div>
            <div className="relative">
              <pre className="code-block scrollbar-thin">
                <code className={`language-${language}`}>
                  {codeExample.after}
                </code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeExample;