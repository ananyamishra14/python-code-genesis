
import React from 'react';
import { Card, CardContent } from "@/components/ui/card";

const HowItWorks = () => {
  const steps = [
    {
      title: "Submit Your Problem",
      description: "Instead of hiring freelancers, just tell us your goal like 'Get 10K legit website visitors'",
      icon: "🎯"
    },
    {
      title: "AI Task Decomposition",
      description: "Our AI breaks down your problem into smaller, manageable tasks",
      icon: "🤖"
    },
    {
      title: "Smart Matching",
      description: "Tasks are matched with qualified micro-contractors",
      icon: "🔄"
    },
    {
      title: "Execution & Management",
      description: "We manage the entire process, ensuring quality results",
      icon: "✅"
    }
  ];

  return (
    <section className="my-16">
      <h2 className="text-3xl font-bold text-center mb-10">How It Works</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {steps.map((step, index) => (
          <Card key={index} className="border-0 shadow-md hover:shadow-lg transition-shadow">
            <CardContent className="pt-6">
              <div className="text-4xl mb-4 flex justify-center">{step.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-center">{step.title}</h3>
              <p className="text-gray-600 text-center">{step.description}</p>
              
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute right-0 top-1/2 transform translate-x-1/2 -translate-y-1/2 text-2xl text-gray-300">
                  →
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      
      <div className="mt-12 text-center">
        <div className="inline-flex items-center px-4 py-2 bg-indigo-100 text-indigo-800 rounded-full">
          <span className="font-medium">Tech Stack:</span>
          <span className="ml-2">AutoGPT-style agents, Stripe Connect, Smart Contracts</span>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
