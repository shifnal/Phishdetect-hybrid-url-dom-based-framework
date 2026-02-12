const fs = require("fs");
const puppeteer = require("puppeteer");

async function extractDOM(url, outputFile) {
  console.log("PUPPETEER START:", url);

  const browser = await puppeteer.launch({
    headless: "new",
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  try {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

    const domTree = await page.evaluate(() => {
      function traverse(node) {
        return {
          tag: node.tagName,
          children: [...node.children].map(traverse),
        };
      }
      return {
        title: document.title,
        dom: traverse(document.body)
      };
    });

    const screenshotPath = outputFile.replace('.json', '.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });

    fs.writeFileSync(outputFile, JSON.stringify(domTree, null, 2));
    console.log("PUPPETEER SUCCESS:", outputFile);

  } catch (err) {
    console.error("PUPPETEER ERROR:", err);
  } finally {
    await browser.close();
  }
}

const url = process.argv[2];
const outputFile = process.argv[3];
extractDOM(url, outputFile);
