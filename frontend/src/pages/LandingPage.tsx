import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { TrendingUp, FileText, BarChart4, LineChart, PieChart, Zap, Shield, Database } from 'lucide-react';

const LandingPage: React.FC = () => {
  // Animation controls
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
      },
    },
  };

  const features = [
    {
      icon: <BarChart4 className="h-10 w-10 text-indigo-500" />,
      title: 'Real-time Stock Analysis',
      description: 'Get instant insights on stock performance with AI-powered analysis of market trends.',
    },
    {
      icon: <LineChart className="h-10 w-10 text-indigo-500" />,
      title: 'Predictive Analytics',
      description: 'Advanced algorithms predict future stock movements with probabilistic consistency.',
    },
    {
      icon: <FileText className="h-10 w-10 text-indigo-500" />,
      title: 'Document Analysis',
      description: 'Upload financial documents for AI-powered analysis and extraction of key insights.',
    },
    {
      icon: <PieChart className="h-10 w-10 text-indigo-500" />,
      title: 'Portfolio Optimization',
      description: 'Optimize your investment portfolio based on risk tolerance and market conditions.',
    },
    {
      icon: <Zap className="h-10 w-10 text-indigo-500" />,
      title: 'Real-time News Analysis',
      description: 'Stay updated with the latest market news and their potential impact on your investments.',
    },
    {
      icon: <Shield className="h-10 w-10 text-indigo-500" />,
      title: 'Risk Assessment',
      description: 'Comprehensive risk analysis to help you make informed investment decisions.',
    },
  ];

  return (
    <div className="pt-20">
      {/* Hero Section */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="py-20 text-center"
      >
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto px-4"
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            AI-Powered Stock Analysis & Prediction
          </h1>
          <p className="text-xl text-gray-300 mb-10">
            Make smarter investment decisions with our advanced AI algorithms that analyze market trends,
            financial documents, and news in real-time.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link to="/dashboard" className="btn-primary">
              <span className="flex items-center justify-center gap-2">
                <TrendingUp size={20} />
                Explore Dashboard
              </span>
            </Link>
            <Link to="/document-analysis" className="btn-secondary">
              <span className="flex items-center justify-center gap-2">
                <FileText size={20} />
                Analyze Documents
              </span>
            </Link>
          </div>
        </motion.div>

        {/* Animated Chart Background */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 1 }}
          className="mt-16 relative h-64 overflow-hidden rounded-xl max-w-5xl mx-auto"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-900/80 to-purple-900/80 z-10 rounded-xl"></div>
          <div className="absolute inset-0 flex items-center justify-center z-20">
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ repeat: Infinity, duration: 3 }}
              className="text-center"
            >
              <h3 className="text-2xl font-bold text-white mb-2">Powered by Advanced AI</h3>
              <p className="text-gray-300">Analyzing millions of data points to deliver accurate predictions</p>
            </motion.div>
          </div>
          <div className="absolute inset-0 z-0">
            <svg width="100%" height="100%" viewBox="0 0 1200 300" preserveAspectRatio="none">
              <path
                d="M0,100 C150,200 350,0 500,100 C650,200 850,0 1000,100 C1150,200 1350,0 1500,100 L1500,300 L0,300 Z"
                className="fill-indigo-600/20"
              ></path>
              <path
                d="M0,100 C150,180 350,20 500,100 C650,180 850,20 1000,100 C1150,180 1350,20 1500,100 L1500,300 L0,300 Z"
                className="fill-purple-600/20"
              ></path>
              <path
                d="M0,100 C150,160 350,40 500,100 C650,160 850,40 1000,100 C1150,160 1350,40 1500,100 L1500,300 L0,300 Z"
                className="fill-pink-600/20"
              ></path>
            </svg>
          </div>
        </motion.div>
      </motion.section>

      {/* Features Section */}
      <motion.section
        ref={ref}
        variants={containerVariants}
        initial="hidden"
        animate={controls}
        className="py-20 bg-gray-900/50 rounded-3xl my-16"
      >
        <div className="container mx-auto px-4">
          <motion.div variants={itemVariants} className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Our platform combines cutting-edge AI technology with financial expertise to provide you with the most
              accurate market insights.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={itemVariants}
                className="card hover:bg-gray-800/80 hover:border border-gray-700 hover:translate-y-[-5px]"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* How It Works Section */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="py-20"
      >
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Our AI-powered platform processes vast amounts of financial data to provide you with actionable insights.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              whileHover={{ y: -5 }}
              className="card text-center"
            >
              <div className="w-16 h-16 bg-indigo-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                <Database className="h-8 w-8 text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">1. Data Collection</h3>
              <p className="text-gray-400">
                Our system collects real-time data from multiple sources including market feeds, financial news, and
                company reports.
              </p>
            </motion.div>

            <motion.div
              whileHover={{ y: -5 }}
              className="card text-center"
            >
              <div className="w-16 h-16 bg-purple-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">2. AI Analysis</h3>
              <p className="text-gray-400">
                Advanced AI algorithms process and analyze the data, identifying patterns and trends that humans might
                miss.
              </p>
            </motion.div>

            <motion.div
              whileHover={{ y: -5 }}
              className="card text-center"
            >
              <div className="w-16 h-16 bg-pink-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                <TrendingUp className="h-8 w-8 text-pink-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">3. Actionable Insights</h3>
              <p className="text-gray-400">
                Receive clear, actionable insights and predictions to help you make informed investment decisions.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="py-20 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-3xl my-16"
      >
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Transform Your Investment Strategy?</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-10">
            Join thousands of investors who are already leveraging our AI-powered platform to make smarter investment
            decisions.
          </p>
          <Link to="/dashboard" className="btn-primary">
            <span className="flex items-center justify-center gap-2">
              <TrendingUp size={20} />
              Get Started Now
            </span>
          </Link>
        </div>
      </motion.section>
    </div>
  );
};

export default LandingPage;