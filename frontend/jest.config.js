module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  moduleFileExtensions: ['ts', 'html', 'js', 'json', 'mjs'],
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@angular/common/locales/.*\\.js$))',
  ],
  transform: {
    '^.+\\.(ts|mjs|js|html)$': [
      'jest-preset-angular',
      {
        tsconfig: '<rootDir>/tsconfig.spec.json',
        stringifyContentPathRegex: '\\.(html|svg)$',
      },
    ],
  },
  testPathIgnorePatterns: ['<rootDir>/node_modules/'],
};
