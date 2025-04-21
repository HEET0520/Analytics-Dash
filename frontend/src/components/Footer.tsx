import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Github, Twitter, Linkedin } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <TrendingUp className="h-6 w-6 text-indigo-500" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
                FinanceAI
              </span>
            </div>
            <p className="text-gray-400 text-sm">
              AI-powered equity market analysis and stock prediction with probabilistic consistency.
            </p>
            <div className="flex space-x-4 mt-4">
              <motion.a
                whileHover={{ y: -3 }}
                className="text-gray-400 hover:text-indigo-500"
                href="#"
                aria-label="Github"
              >
                <Github size={20} />
              </motion.a>
              <motion.a
                whileHover={{ y: -3 }}
                className="text-gray-400 hover:text-indigo-500"
                href="#"
                aria-label="Twitter"
              >
                <Twitter size={20} />
              </motion.a>
              <motion.a
                whileHover={{ y: -3 }}
                className="text-gray-400 hover:text-indigo-500"
                href="#"
                aria-label="LinkedIn"
              >
                <Linkedin size={20} />
              </motion.a>
            </div>
          </div>

          <div className="col-span-1">
            <h3 className="text-white font-medium mb-4">Features</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Stock Analysis
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Market Predictions
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Document Analysis
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Financial News
                </a>
              </li>
            </ul>
          </div>

          <div className="col-span-1">
            <h3 className="text-white font-medium mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  API Reference
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Support
                </a>
              </li>
            </ul>
          </div>

          <div className="col-span-1">
            <h3 className="text-white font-medium mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Cookie Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-400 hover:text-indigo-400 text-sm">
                  Disclaimer
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-6 text-center">
          <p className="text-gray-500 text-sm">
            © {new Date().getFullYear()} FinanceAI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;