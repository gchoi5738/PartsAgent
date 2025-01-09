import React from 'react';

const FAQ = () => {
  const faqs = [
    {
      question: 'What is your return policy?',
      answer: 'We offer a 30-day return policy for all unopened parts. For opened parts, we accept returns within 14 days if the part is in its original condition.'
    },
    {
      question: 'How long does shipping take?',
      answer: 'Standard shipping typically takes 3-5 business days. Express shipping (2-day) and Next-day shipping options are available for most items.'
    },
    {
      question: 'Do you offer installation support?',
      answer: 'Yes! We provide detailed installation guides and video tutorials for all our parts. Our chat support can also help with installation questions.'
    },
    {
      question: 'Are your parts genuine/OEM?',
      answer: 'Yes, we offer both genuine OEM parts and high-quality aftermarket alternatives. All parts are clearly labeled as either OEM or aftermarket.'
    },
    {
      question: 'What warranty do you offer?',
      answer: 'All parts come with a minimum 90-day warranty. Many parts have extended warranties of up to one year. Warranty information is listed on each product page.'
    }
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Frequently Asked Questions</h1>
      <div className="space-y-6">
        {faqs.map((faq, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-2">{faq.question}</h3>
            <p className="text-gray-600">{faq.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FAQ;