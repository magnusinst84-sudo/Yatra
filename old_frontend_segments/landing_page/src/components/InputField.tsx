import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

interface InputFieldProps {
  label: string;
  type: 'text' | 'email' | 'password';
  id: string;
  placeholder: string;
  icon: React.ReactNode;
}

export const InputField: React.FC<InputFieldProps> = ({
  label,
  type,
  id,
  placeholder,
  icon,
}) => {
  const [showPassword, setShowPassword] = useState(false);

  // Toggle dynamic password type
  const inputType = type === 'password' && showPassword ? 'text' : type;

  return (
    <div className="flex flex-col gap-1.5 w-full text-left">
      {/* Label */}
      <label htmlFor={id} className="text-[10px] font-sans font-semibold tracking-wider text-gold-light/70 uppercase">
        {label}
      </label>

      {/* Field Container */}
      <div className="relative flex items-center w-full">
        {/* Leading Icon wrapper */}
        <div className="absolute left-4 text-gray-500 pointer-events-none flex items-center justify-center">
          {icon}
        </div>

        {/* Input */}
        <input
          id={id}
          type={inputType}
          placeholder={placeholder}
          className="w-full pl-11 pr-11 py-3 bg-cinematic-900/65 backdrop-blur-md border border-white/5 hover:border-white/10 focus:border-gold/55 focus:shadow-gold-glow rounded-xl text-sm text-white placeholder-gray-500 font-sans tracking-wide outline-none transition-all duration-300"
        />

        {/* Password Eye Toggle */}
        {type === 'password' && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 text-gray-500 hover:text-gold transition-colors flex items-center justify-center outline-none"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        )}
      </div>
    </div>
  );
};
