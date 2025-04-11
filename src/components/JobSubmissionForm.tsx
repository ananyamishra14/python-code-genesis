
import React, { useState } from 'react';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { CheckCircle, Loader2 } from "lucide-react";

const JobSubmissionForm = () => {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    budget: [500],
    timeline: [30],
    examples: '',
    goals: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSliderChange = (name: string, value: number[]) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      toast({
        title: "Problem submitted successfully!",
        description: "Our AI is now analyzing your request and breaking it down into tasks.",
      });
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        budget: [500],
        timeline: [30],
        examples: '',
        goals: ''
      });
      setStep(1);
    }, 2000);
  };

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <Label htmlFor="title">What do you want to achieve?</Label>
            <Input
              id="title"
              name="title"
              placeholder="e.g., Get 10K legit website visitors"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </div>
          
          <div>
            <Label htmlFor="description">Describe your problem in detail</Label>
            <Textarea
              id="description"
              name="description"
              placeholder="Tell us more about what you're trying to accomplish..."
              value={formData.description}
              onChange={handleChange}
              rows={5}
              required
            />
          </div>
          
          <Button type="button" onClick={nextStep} className="w-full">
            Continue to Budget & Timeline
          </Button>
        </div>
      )}
      
      {step === 2 && (
        <div className="space-y-4">
          <div>
            <Label htmlFor="budget">Budget (USD)</Label>
            <div className="flex items-center space-x-4">
              <Slider
                id="budget"
                name="budget"
                value={formData.budget}
                onValueChange={(value) => handleSliderChange('budget', value)}
                min={100}
                max={10000}
                step={100}
              />
              <span className="w-16 text-right">${formData.budget[0]}</span>
            </div>
          </div>
          
          <div>
            <Label htmlFor="timeline">Timeline (Days)</Label>
            <div className="flex items-center space-x-4">
              <Slider
                id="timeline"
                name="timeline"
                value={formData.timeline}
                onValueChange={(value) => handleSliderChange('timeline', value)}
                min={1}
                max={90}
                step={1}
              />
              <span className="w-16 text-right">{formData.timeline[0]} days</span>
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button type="button" variant="outline" onClick={prevStep}>
              Back
            </Button>
            <Button type="button" onClick={nextStep} className="flex-1">
              Continue to Examples & Goals
            </Button>
          </div>
        </div>
      )}
      
      {step === 3 && (
        <div className="space-y-4">
          <div>
            <Label htmlFor="examples">Examples or references (Optional)</Label>
            <Textarea
              id="examples"
              name="examples"
              placeholder="Share examples of what you're trying to achieve..."
              value={formData.examples}
              onChange={handleChange}
              rows={3}
            />
          </div>
          
          <div>
            <Label htmlFor="goals">Success criteria - How will you measure success? (Optional)</Label>
            <Textarea
              id="goals"
              name="goals"
              placeholder="e.g., At least 10K unique visitors verified by Google Analytics..."
              value={formData.goals}
              onChange={handleChange}
              rows={3}
            />
          </div>
          
          <div className="flex space-x-2">
            <Button type="button" variant="outline" onClick={prevStep}>
              Back
            </Button>
            <Button type="submit" disabled={isSubmitting} className="flex-1">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Submit Problem
                </>
              )}
            </Button>
          </div>
        </div>
      )}
      
      <div className="mt-4">
        <div className="flex justify-between">
          <div className={`h-2 w-1/3 rounded-l-full ${step >= 1 ? 'bg-indigo-600' : 'bg-gray-200'}`}></div>
          <div className={`h-2 w-1/3 ${step >= 2 ? 'bg-indigo-600' : 'bg-gray-200'}`}></div>
          <div className={`h-2 w-1/3 rounded-r-full ${step >= 3 ? 'bg-indigo-600' : 'bg-gray-200'}`}></div>
        </div>
        <div className="mt-2 text-sm text-gray-500 text-center">
          Step {step} of 3
        </div>
      </div>
    </form>
  );
};

export default JobSubmissionForm;
